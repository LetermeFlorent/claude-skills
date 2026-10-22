import argparse
import datetime
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import DECODE_ERRORS, ENCODING, guard, refuse, short, write_text
from plan import CONSTRAINTS, body, section, tasks
from repo import dirty, find_root, head, project_name, tree_of
from space import IGNORED, TASK_ID, folder_for, load_record, named, save_record, temp_root

FINAL = "final"


def _text(lines, task_id):
    found = {task["number"]: task for task in tasks(lines)}
    wanted = [int(part) for part in task_id.split(",")]
    missing = [number for number in wanted if number not in found]
    if missing:
        known = ", ".join(str(number) for number in sorted(found)) or "none"
        refuse([f"no heading 'Task {number}' in the plan (tasks found: {known})" for number in missing])
    parts = ["\n".join(body(lines, found[number])).rstrip() for number in wanted]
    constraints = "\n".join(section(lines, CONSTRAINTS)).rstrip()
    return "\n\n".join(parts + ([constraints] if constraints else [])) + "\n"


def _record(folder, task_id, root, restart):
    record = load_record(folder, task_id)
    if record and not restart:
        return record, f"record kept, started at {short(record['base'])}, {len(record['snapshots'])} package(s)"
    base = head(root)
    record = {"id": task_id, "root": root.as_posix(), "base": base, "base_tree": tree_of(root, base),
              "dirty": sorted(path for path in dirty(root) if not path.startswith(IGNORED)), "snapshots": [],
              "started": datetime.datetime.now().isoformat(timespec="seconds")}
    save_record(folder, task_id, record)
    return record, f"record created at {short(base)}"


def main():
    parser = argparse.ArgumentParser(description="Write one task's brief and record where the task starts.")
    parser.add_argument("plan")
    parser.add_argument("task", help="a task number, numbers joined by commas for a batch, or final")
    parser.add_argument("--restart", action="store_true", help="forget the task's packages and start from HEAD")
    args = parser.parse_args()
    plan = Path(args.plan).resolve()
    if not plan.is_file():
        refuse([f"no plan file at {plan.as_posix()}"])
    if not TASK_ID.match(args.task):
        refuse([f"task id {args.task!r}: a number, numbers joined by commas, or final"])
    root = find_root(Path.cwd())
    folder = folder_for(temp_root(), project_name(root), plan)
    folder.mkdir(parents=True, exist_ok=True)
    if args.task == FINAL:
        print("brief: none for the final fix wave, hand the fixer the final review file")
    else:
        lines = plan.read_text(encoding=ENCODING, errors=DECODE_ERRORS).splitlines()
        brief = named(folder, args.task, "-brief.md")
        write_text(brief, _text(lines, args.task))
        print(f"brief: {brief.as_posix()}")
    record, state = _record(folder, args.task, root, args.restart)
    print(f"report: {named(folder, args.task, '-report.md').as_posix()}")
    print(state)
    print(f"paths already changed before the task: {len(record['dirty'])}"
          + (f" ({', '.join(record['dirty'][:8])})" if record["dirty"] else ""))


if __name__ == "__main__":
    guard(main, "copy the task's section of the plan into a file of the workspace by hand, and note git rev-parse HEAD")
