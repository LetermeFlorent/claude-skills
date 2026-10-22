import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import FAILED, REFUSED, guard, refuse, short, write_text
from repo import diff, find_root, project_name, snapshot
from rows import changed_lines, from_measure, from_scan, show, split
from space import TASK_ID, folder_for, gate_path, load_record, named, task_paths, temp_root
from tools import MEASURE, SCAN, locate, measure, scan

SKILL = HERE.parent
SHOWN = 25


def _measure(args, root, problems):
    script, tried = locate("clean-code", args.clean_code, SKILL, MEASURE)
    if script is None:
        problems.append(f"clean-code measure not found in {', '.join(tried)}")
        return []
    findings, problem = measure(root, root / args.scope if args.scope else root, script)
    if problem:
        problems.append(f"clean-code measure failed: {problem}")
    return from_measure(findings or [])


def _scan(args, root, changes, problems):
    script, tried = locate("anti-empreinte", args.anti_empreinte, SKILL, SCAN)
    if script is None:
        problems.append(f"anti-empreinte scan not found in {', '.join(tried)}")
        return []
    output, failures = scan(root, [path for path in changes if (root / path).is_file()], script)
    problems.extend(f"anti-empreinte scan failed on {failure}" for failure in failures)
    return from_scan(output)


def _write(out, title, groups):
    counted, aside, problems = groups
    blocks = [f"# Gate, {title}", "", "## Rows on lines this task wrote", *map(show, counted), "",
              "## Left aside, lines the task did not write", *map(show, aside), "", "## Could not run", *problems, ""]
    write_text(out, "\n".join(blocks))


def _check(args, folder):
    record = load_record(folder, args.task)
    if record is None:
        refuse([f"no record for task {args.task}: run brief.py first"])
    root = Path(record["root"])
    paths, _, problems = task_paths(record, root, args.paths)
    if problems:
        refuse(problems)
    tree = snapshot(root, record["base"], paths, named(folder, args.task, ".gate.index"))
    changes = changed_lines(diff(root, record["base_tree"], tree, "-U0"))
    if not changes:
        refuse(["the listed paths hold no change since the task started"])
    problems = []
    rows = _measure(args, root, problems) + _scan(args, root, changes, problems)
    counted, aside = split(rows, changes)
    out = gate_path(folder, args.task, tree)
    _write(out, f"task {args.task} at {short(tree)}", (counted, aside, problems))
    return counted, aside, problems, out


def main():
    parser = argparse.ArgumentParser(description="Run the clean-code measure and the anti-empreinte scan on the "
                                                 "lines one task wrote.")
    parser.add_argument("plan")
    parser.add_argument("task")
    parser.add_argument("--paths", nargs="+", required=True, help="every path the task created, edited or deleted")
    parser.add_argument("--scope", help="folder to measure, relative to the repository, when the whole repo is big")
    parser.add_argument("--clean-code", help="folder of the clean-code skill")
    parser.add_argument("--anti-empreinte", help="folder of the anti-empreinte skill")
    args = parser.parse_args()
    plan = Path(args.plan).resolve()
    if not plan.is_file() or not TASK_ID.match(args.task):
        refuse([f"give an existing plan file and a task id, got {plan.as_posix()} and {args.task!r}"])
    folder = folder_for(temp_root(), project_name(find_root(Path.cwd())), plan)
    counted, aside, problems, out = _check(args, folder)
    print(f"gate: {len(counted)} rows on lines this task wrote" if counted else "gate: clean")
    for row in counted[:SHOWN]:
        print(f"  {show(row)}")
    if len(counted) > SHOWN:
        print(f"  {len(counted) - SHOWN} more in the gate file")
    print(f"left aside: {len(aside)} rows on lines the task did not write")
    for problem in problems:
        print(f"could not run: {problem}")
    print(f"gate file: {out.as_posix()}")
    if counted:
        sys.exit(REFUSED)
    if problems:
        sys.exit(FAILED)


if __name__ == "__main__":
    guard(main, "python -I <clean-code>/scripts/measure.py . and python -I <anti-empreinte>/scripts/scan.py <file> "
                "--no-git on each path, then keep the rows on the lines the task wrote")
