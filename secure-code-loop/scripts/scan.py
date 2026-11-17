import argparse
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent / "lib"))

import findings
import project
import tools
from cleanup import test_changes
from common import (ADVISORIES, FALSE_POSITIVES, FINDINGS_FILE, HISTORY_FILE, START_FILE, guard, read_json, read_lines,
                    refuse, work_folder, write_json)

HINT = f'python -I "{HERE.as_posix()}" --work "<work folder>" --passed <n> --failed <n>'
LIMIT, WINDOW, ROW_LIMIT = 5, 3, 40
BLOAT_LIMIT, PERCENT = 0.3, 100
STOP, CONTINUE = "stop", "continue"
ITERATION = "iteration-{}"
UNREADABLE = (AttributeError, KeyError, TypeError, ValueError)


def arguments():
    parser = argparse.ArgumentParser(description="Run every scanner found, merge the findings, say whether to stop.")
    parser.add_argument("--work", required=True, help="work folder printed by start.py")
    parser.add_argument("--passed", type=int, required=True, help="tests passed in the run just before this scan")
    parser.add_argument("--failed", type=int, required=True, help="tests failed or in error in that run")
    parser.add_argument("--offline", action="store_true", help="no rule, database or advisory download")
    parser.add_argument("--rules", help="local Semgrep rules folder, used instead of the registry packs")
    parser.add_argument("--timeout", type=int, default=tools.DEFAULT_TIMEOUT, help="seconds per scanner run")
    return parser.parse_args()


def load(options):
    work = work_folder(options.work)
    reasons = [] if work else [f"{options.work} is not a work folder printed by start.py"]
    reasons += [] if min(options.passed, options.failed) >= 0 else ["--passed and --failed count tests, 0 or more"]
    reasons += [] if options.timeout > 0 else ["--timeout is in seconds, more than 0"]
    rules = Path(options.rules).resolve() if options.rules else None
    reasons += [f"{options.rules} is not a folder"] if rules and not rules.is_dir() else []
    if reasons:
        refuse(reasons)
    return work, read_json(work / START_FILE), rules


def raws_of(runs, folder):
    found = []
    for entry in runs:
        data = read_json(folder / entry["file"]) if entry["state"].startswith(tools.OK) else None
        if data is None:
            continue
        try:
            parsed = tools.BY_NAME[entry["tool"]].parser(data, entry["place"])
        except UNREADABLE as error:
            entry["state"] = f"failed: unreadable output, {type(error).__name__}"
            continue
        found += [raw._replace(tool=entry["tool"]) for raw in parsed]
    return found


def decide(history):
    now, first = history[-1], history[0]
    worse = now["failed"] > first["failed"] or now["passed"] < first["passed"]
    notes = ", tests worse than iteration 1" * worse + ", old tests touched" * bool(now.get("touched"))
    if not now["ran"]:
        return STOP, "no scanner ran"
    if not now["blocking"] and not notes:
        return STOP, "clean"
    if len(history) >= LIMIT:
        return STOP, f"limit of {LIMIT} iterations"
    window = [entry["blocking"] for entry in history[-WINDOW:]]
    if len(window) == WINDOW and all(later >= earlier for earlier, later in zip(window, window[1:])):
        return STOP, f"stalled, no drop in blocking over {WINDOW - 1} iterations"
    return CONTINUE, f"{now['blocking']} blocking in scope{notes}"


def growth(root, start, scope):
    now = {name: project.line_count(root / name) for name in scope if project.is_code(name)}
    return sum((start.get("lines") or {}).get(name, 0) for name in now), sum(now.values())


def bloat_lines(before, after):
    if not before:
        return [f"lines: {after} in scope code, none at start"]
    change = (after - before) / before
    lines = [f"lines: {before} -> {after} in scope code ({change * PERCENT:+.0f}%)"]
    if change > BLOAT_LIMIT:
        lines.append(f"bloat: over {BLOAT_LIMIT * PERCENT:.0f}%, share one helper instead of copies, drop extra checks")
    return lines


def rows(buckets):
    scope = buckets[findings.SCOPE]
    listed = [f"fix: {findings.row(item)}" for item in findings.blocking(scope)]
    listed += [f"revoke: {findings.row(item)}" for item in buckets[findings.REVOKE]]
    listed += [f"also: {findings.row(item)}" for item in scope if item["level"] not in findings.BLOCKING]
    listed += [f"elsewhere: {findings.row(item)}" for item in findings.blocking(buckets[findings.ELSEWHERE])]
    extra = len(listed) - ROW_LIMIT
    return listed[:ROW_LIMIT] + ([f"more: {extra} rows in {FINDINGS_FILE}"] if extra > 0 else [])


def scanned(work, start, options, folder):
    root, is_git = Path(start["root"]), start["is_git"]
    names = project.files(root, is_git)
    present, scope = set(names), set(project.scope_files(root, start, names))
    runs = tools.run_all(tools.Context(root, names, is_git, options.offline, options.rules, options.timeout), folder)
    dismissed, bad = findings.false_positives(read_lines(work / FALSE_POSITIVES))
    entries, wrong = findings.advisories(read_lines(work / ADVISORIES), present)
    raws = raws_of(runs, folder) + findings.advisory_raws(entries)
    buckets = findings.split(findings.merge_all(raws, root), scope, present, dismissed)
    lines = [f"tool: {run['tool']} {run['place']} {run['state']}" for run in runs]
    gaps = tools.not_covered(runs, names)
    lines += [f"not covered: {', '.join(gaps)}"] if gaps else []
    lines += [f"bad line: {FALSE_POSITIVES}: {line}" for line in bad]
    lines += [f"bad line: {ADVISORIES}: {line}" for line in wrong]
    lines += rows(buckets) + bloat_lines(*growth(root, start, scope))
    changed, missing = test_changes(root, start)
    lines += [f"changed test: {name}" for name in changed] + [f"missing test: {name}" for name in missing]
    return runs, buckets, lines, (len(scope), len(changed) + len(missing))


def main():
    options = arguments()
    work, start, options.rules = load(options)
    history = read_json(work / HISTORY_FILE) or []
    iteration = len(history) + 1
    folder = work / ITERATION.format(iteration)
    folder.mkdir(exist_ok=True)
    runs, buckets, lines, (size, touched) = scanned(work, start, options, folder)
    counts = {name: len(items) for name, items in buckets.items()}
    history.append({"iteration": iteration, "ran": sum(run["state"].startswith(tools.OK) for run in runs),
                    "blocking": len(findings.blocking(buckets[findings.SCOPE])), "counts": counts,
                    "levels": dict(Counter(item["level"] for item in buckets[findings.SCOPE])),
                    "passed": options.passed, "failed": options.failed, "touched": touched})
    write_json(folder / FINDINGS_FILE, {"runs": runs, "buckets": buckets})
    write_json(work / HISTORY_FILE, history)
    print(f"iteration: {iteration}, scope: {size} files")
    for line in lines:
        print(line)
    print("found: " + ", ".join(f"{name} {count}" for name, count in counts.items()))
    print(f"tests: passed {options.passed} failed {options.failed}, iteration 1: passed {history[0]['passed']} "
          f"failed {history[0]['failed']}")
    print("{}: {}".format(*decide(history)))


if __name__ == "__main__":
    guard(main, HINT)
