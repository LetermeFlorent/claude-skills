import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import guard, read_json, write_json
from runs import FINDINGS, MEASURE, SCORE, latest_run, project_root, run_help, runs
from store import CANDIDATE, CONFIRMED, REFUTED

TOP = 100
STEP = 1
EACH = {2: 2.5, 3: 1, 4: 1, 5: 2.5, 6: 1, 7: 1, 8: 1, 9: 2.5, 10: 2.5, 11: 2.5, 12: 5, 13: 1, 16: 1, 17: 1, 19: 1}
SHARE = {14: ("comment_scanned", 10), 15: ("named_files", 10), 18: ("valued_files", 10)}
LONG_FILES = 1
CURVE = ((0.1, 2.5), (0.4, 15))
CAPS = {"secret": 25, "build": 40, "swallowed": 50, "test-in-prod": 50, "attribution": 50}
READ_RULES = (2, 5, 7, 9, 11, 16)
SHOWN = 20
DIGITS = 2


def _curve(share):
    (low, least), (high, most) = CURVE
    if share <= low:
        return least
    return least + (share - low) / (high - low) * (most - least)


def deductions(confirmed, stats):
    by_rule = defaultdict(list)
    for finding in confirmed:
        by_rule[finding["rule"]].append(finding)
    taken = {}
    for rule, found in sorted(by_rule.items()):
        files = {finding["file"] for finding in found}
        if rule == 0:
            taken[rule] = sum(finding.get("points", 0) for finding in found)
        elif rule == LONG_FILES:
            taken[rule] = _curve(len(files) / max(stats.get("code_files", 0), len(files)))
        elif rule in SHARE:
            key, most = SHARE[rule]
            taken[rule] = most * len(files) / max(stats.get(key, 0), len(files))
        else:
            taken[rule] = EACH[rule] * len(found)
    return taken


def _ready(payload):
    pending = [finding["id"] for finding in payload["findings"] if finding["status"] == CANDIDATE]
    if pending:
        more = f" and {len(pending) - SHOWN} more" if len(pending) > SHOWN else ""
        raise ValueError(f"{len(pending)} findings still without a verdict: {', '.join(pending[:SHOWN])}{more}")
    covered = {finding["rule"] for finding in payload["findings"]}
    covered |= {entry["rule"] for entry in payload.get("checked", []) + payload.get("unmeasured", [])}
    missing = [str(rule) for rule in READ_RULES if rule not in covered]
    if missing:
        raise ValueError(f"rules {', '.join(missing)} never read: add findings, or declare them with "
                         "findings.py checked or findings.py unmeasured")


def _previous(root, run):
    earlier = [folder for folder in runs(root) if folder.name < run.name and (folder / SCORE).exists()]
    return read_json(earlier[-1] / SCORE) if earlier else None


def _rounded(value):
    return math.floor(round(value / STEP, 9)) * STEP


def report(score, confirmed, previous):
    print(f"note: {score['note']:g}/{TOP}")
    cap = score["cap"]
    capped = f", capped at {cap['value']} by {cap['name']} ({cap['id']})" if cap else ""
    print(f"deductions: {score['total']:g} from {TOP}{capped}")
    print(" | ".join(f"rule {rule}: {points:g}" for rule, points in score["deductions"].items()) or "no deduction")
    for entry in score["unmeasured"]:
        print(f"not measured: rule {entry['rule']}, {entry['why']}")
    if previous and previous.get("top") == TOP:
        print(f"previous run {previous['run']}: {previous['note']:g}/{TOP}, now {score['note']:g}/{TOP} "
              f"({score['note'] - previous['note']:+g})")
    for finding in confirmed:
        print(f"{finding['id']} | {finding['rule']} | {finding['what']} | {finding['file']}:{finding['line']} | "
              f"{finding['proof']}")
    if score["note"] == TOP:
        print("nothing to fix: no plan, no question")


def main():
    parser = argparse.ArgumentParser(description="Compute the note out of 100 from the verified findings of a run.")
    parser.add_argument("--run", help=run_help())
    args = parser.parse_args()
    root = project_root(Path.cwd())
    run = latest_run(root, args.run)
    payload = read_json(run / FINDINGS)
    stats = read_json(run / MEASURE)["stats"]
    _ready(payload)
    confirmed = [finding for finding in payload["findings"] if finding["status"] == CONFIRMED]
    taken = deductions(confirmed, stats)
    caps = sorted((CAPS[f["cap"]], f["cap"], f["id"]) for f in confirmed if f.get("cap"))
    total = sum(taken.values())
    note = _rounded(min([TOP - total] + [value for value, _, _ in caps[:1]]))
    score = {"run": run.name, "top": TOP, "note": note, "total": round(total, DIGITS),
             "deductions": {rule: round(points, DIGITS) for rule, points in taken.items()},
             "cap": dict(zip(("value", "name", "id"), caps[0])) if caps else None,
             "unmeasured": payload.get("unmeasured", []), "confirmed": len(confirmed),
             "refuted": sum(finding["status"] == REFUTED for finding in payload["findings"])}
    write_json(run / SCORE, score)
    report(score, confirmed, _previous(root, run))


if __name__ == "__main__":
    guard(main, "start from 100, take off the points of SKILL.md for each confirmed finding, keep the lowest cap")
