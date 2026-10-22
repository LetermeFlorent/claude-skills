import argparse
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import guard
from runs import latest_run, project_root
from store import CANDIDATE, CAPS, CONFIRMED, LISTS, NO_CAP, REFUTED, SECRET, opened

RULES = range(20)
STATUS = {"confirm": CONFIRMED, "refute": REFUTED}
MAX_POINTS = 3


def show(payload, args):
    shown = [f for f in payload["findings"] if (not args.status or f["status"] == args.status)
             and (args.rule is None or f["rule"] == args.rule)]
    for finding in shown:
        why = f" | {finding['why']}" if finding.get("why") else ""
        print(f"{finding['id']} | {finding['status']} | {finding['rule']} | {finding['file']}:{finding['line']} | "
              f"{finding['what']} | {finding['proof']}{why}")
    for kind in LISTS:
        for entry in payload[kind]:
            print(f"rule {entry['rule']} {kind}: {entry['why']}")
    counts = Counter(f["status"] for f in payload["findings"])
    print(", ".join(f"{status}: {count}" for status, count in sorted(counts.items())) or "no findings")


def add(payload, args):
    if args.rule == 0 and args.points is None and args.cap != SECRET:
        raise ValueError("rule 0 needs --points between 0.5 and 3, or --cap secret")
    for finding in payload["findings"]:
        if (finding["rule"], finding["file"], finding["line"]) == (args.rule, args.file, args.line):
            print(f"already there as {finding['id']}: {finding['what']}, not added")
            return
    numbers = [int(f["id"][1:]) for f in payload["findings"] if f["id"].startswith("R")]
    finding = {"id": f"R{max(numbers, default=0) + 1}", "status": CANDIDATE, "source": args.source,
               "rule": args.rule, "file": args.file, "line": args.line, "what": args.what, "proof": args.proof}
    finding.update({key: value for key, value in (("cap", args.cap), ("points", args.points)) if value is not None})
    payload["findings"].append(finding)
    print(f"added {finding['id']}")


def judge(payload, args):
    index = {finding["id"]: finding for finding in payload["findings"]}
    unknown = [wanted for wanted in args.ids if wanted not in index]
    if unknown:
        raise KeyError(f"unknown ids {', '.join(unknown)}, see findings.py list")
    for wanted in args.ids:
        finding = index[wanted]
        finding.update(status=STATUS[args.command], why=args.why)
        if args.cap == NO_CAP:
            finding.pop("cap", None)
        elif args.cap:
            finding["cap"] = args.cap
        if args.points is not None:
            finding["points"] = args.points
    print(f"{STATUS[args.command]}: {', '.join(args.ids)}")


def declare(payload, args):
    key = args.command
    payload[key] = [entry for entry in payload[key] if entry["rule"] != args.rule]
    payload[key].append({"rule": args.rule, "why": args.why})
    print(f"rule {args.rule} {key}: {args.why}")


def points(text):
    value = float(text)
    if not 0 <= value <= MAX_POINTS:
        raise argparse.ArgumentTypeError(f"points go from 0 to {MAX_POINTS}")
    return value


def parser():
    top = argparse.ArgumentParser(description="Read and update the findings of a clean-code run.")
    top.add_argument("--run", help="run folder, defaults to the latest under .ia/clean-code")
    commands = top.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--status", choices=(CANDIDATE, CONFIRMED, REFUTED))
    listing.add_argument("--rule", type=int, choices=RULES)
    adding = commands.add_parser("add")
    adding.add_argument("--rule", type=int, choices=RULES, required=True)
    for name, kind in (("--file", str), ("--line", int), ("--what", str), ("--proof", str)):
        adding.add_argument(name, type=kind, required=True)
    adding.add_argument("--cap", choices=CAPS)
    adding.add_argument("--points", type=points)
    adding.add_argument("--source", default="reader")
    for name in STATUS:
        verdict = commands.add_parser(name)
        verdict.add_argument("ids", nargs="+")
        verdict.add_argument("--why", required=True)
        verdict.add_argument("--cap", choices=CAPS + (NO_CAP,))
        verdict.add_argument("--points", type=points)
    for name in LISTS:
        rule = commands.add_parser(name)
        rule.add_argument("--rule", type=int, choices=RULES, required=True)
        rule.add_argument("--why", required=True)
    return top


def main():
    args = parser().parse_args()
    run = latest_run(project_root(Path.cwd()), args.run)
    actions = {"list": show, "add": add, "confirm": judge, "refute": judge, "checked": declare, "unmeasured": declare}
    with opened(run, save=actions[args.command] is not show) as payload:
        actions[args.command](payload, args)


if __name__ == "__main__":
    guard(main, "edit findings.json in the run folder by hand, one writer at a time")
