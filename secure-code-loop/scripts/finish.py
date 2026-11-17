import argparse
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent / "lib"))

import cleanup
import findings
import project
import tools
from common import (ADVISORIES, FALSE_POSITIVES, FINDINGS_FILE, HISTORY_FILE, START_FILE, guard, read_json, read_lines,
                    refuse, work_folder)
from parsers import LEVELS

HINT = f'python -I "{HERE.as_posix()}" --work "<work folder>" [--close --passed <n> --failed <n>]'
ITERATION = "iteration-{}"
ROW_LIMIT = 40


def arguments():
    parser = argparse.ArgumentParser(description="Delete what the loop created, then print the report material.")
    parser.add_argument("--work", required=True, help="work folder printed by start.py")
    parser.add_argument("--close", action="store_true", help="delete the work folder once nothing is left over")
    parser.add_argument("--passed", type=int, help="with --close: tests passed in the run after this cleanup")
    parser.add_argument("--failed", type=int, help="with --close: tests failed or in error in that run")
    return parser.parse_args()


def levels(entry):
    found = sorted((entry.get("levels") or {}).items(), key=lambda pair: LEVELS.index(pair[0]))
    return ", ".join(f"{level} {count}" for level, count in found) or "none"


def ledgers(work, buckets, names):
    reasons, _ = findings.false_positives(read_lines(work / FALSE_POSITIVES))
    lines = [f"false positive: {findings.row(item)} | {reasons.get(item['key'], '')}"
             for item in buckets.get(findings.DISMISSED) or []]
    entries, _ = findings.advisories(read_lines(work / ADVISORIES), set(names))
    return lines + [f"advisory: {entry['state']} {entry['level']} {entry['id']} {entry['path']}: {entry['note']}"
                    for entry in entries]


def left_open(buckets):
    scope = buckets.get(findings.SCOPE) or []
    listed = [f"remaining: {findings.row(item)}" for item in findings.blocking(scope)]
    listed += [f"elsewhere: {findings.row(item)}" for item in findings.blocking(buckets.get(findings.ELSEWHERE) or [])]
    other = len(scope) - len(findings.blocking(scope))
    extra = len(listed) - ROW_LIMIT
    return listed[:ROW_LIMIT] + ([f"more: {extra} rows in {FINDINGS_FILE}"] if extra > 0 else []) + (
        [f"other in scope: {other} medium or lower"] if other else [])


def summary(work, start, history):
    if not history:
        return ["scans: none"]
    first, last = history[0], history[-1]
    data = read_json(work / ITERATION.format(last["iteration"]) / FINDINGS_FILE) or {}
    runs, buckets = data.get("runs") or [], data.get("buckets") or {}
    names = project.files(Path(start["root"]), start["is_git"])
    gaps = tools.not_covered(runs, names)
    lines = [f"iterations: {last['iteration']}",
             f"blocking in scope: {first['blocking']} at iteration 1, {last['blocking']} at the last scan",
             f"scope by level: {levels(first)} at iteration 1; {levels(last)} at the last scan",
             "tools ran: " + (", ".join(sorted({run["tool"] for run in runs if run["state"].startswith(tools.OK)}))
                              or "none"),
             "tools missing: " + (", ".join(sorted({run["tool"] for run in runs if run["state"] == tools.MISSING}))
                                  or "none")]
    lines += [f"not covered: {', '.join(gaps)}"] if gaps else []
    lines += [f"tool: {run['tool']} {run['place']} {run['state']}" for run in runs
              if not run["state"].startswith(tools.OK) and run["state"] != tools.MISSING]
    lines += ledgers(work, buckets, names)
    lines += [f"revoke: {findings.row(item)}" for item in buckets.get(findings.REVOKE) or []]
    return lines + left_open(buckets) + [
        f"tests: passed {first['passed']} failed {first['failed']} at iteration 1, "
        f"passed {last['passed']} failed {last['failed']} at the last scan"]


def close(work, history, problems, options):
    reasons = list(problems)
    if options.passed is None or options.failed is None:
        reasons.append("--close needs --passed and --failed from a test run after this cleanup")
    elif history and (options.failed > history[0]["failed"] or options.passed < history[0]["passed"]):
        reasons.append(f"tests worse than at iteration 1: passed {options.passed} failed {options.failed}, "
                       f"was passed {history[0]['passed']} failed {history[0]['failed']}")
    if reasons:
        refuse(reasons)
    shutil.rmtree(work)
    print(f"closed: {work.as_posix()} deleted")


def main():
    options = arguments()
    work = work_folder(options.work)
    if not work:
        refuse([f"{options.work} is not a work folder printed by start.py"])
    start, history = read_json(work / START_FILE), read_json(work / HISTORY_FILE) or []
    lines = cleanup.clean(Path(start["root"]), start, work)
    for line in lines + summary(work, start, history):
        print(line)
    if options.close:
        close(work, history, cleanup.problems(lines), options)


if __name__ == "__main__":
    guard(main, HINT)
