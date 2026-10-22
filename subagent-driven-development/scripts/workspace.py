import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import DECODE_ERRORS, ENCODING, guard, refuse, short, write_text
from ledger import HEADER, note_problems, parse, pending
from plan import body, files_of, is_hard, shared, spec, tasks
from repo import branch, default_branch, dirty, exclude_file, find_root, head, is_ancestor, project_name
from space import IGNORED, LEDGER, ensure_excluded, folder_for, temp_root

NONE_WORDS = {"none", "n/a", "-"}


def _plan(raw):
    plan = Path(raw).resolve()
    if not plan.is_file():
        refuse([f"no plan file at {plan.as_posix()}"])
    return plan, plan.read_text(encoding=ENCODING, errors=DECODE_ERRORS).splitlines()


def _ledger(folder, plan):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / LEDGER
    if not path.exists():
        write_text(path, HEADER.format(plan=plan.as_posix()) + "\n")
    return path, path.read_text(encoding=ENCODING, errors=DECODE_ERRORS).splitlines()


def _marks(task, part, state, root):
    number, marks = task["number"], ["hard"] if is_hard(task, part) else []
    sha = state["complete"].get(number)
    if sha:
        marks.append(f"done {sha}" + ("" if is_ancestor(root, sha, "HEAD") else ", NOT in this branch"))
    elif number in state["rounds"]:
        marks.append(f"fix round {state['rounds'][number]} in progress")
    return marks


def _tasks(lines, state, root):
    found, files = tasks(lines), {}
    print(f"tasks: {len(found)}")
    for task in found:
        part = body(lines, task)
        files[task["number"]] = files_of(part)
        marks = _marks(task, part, state, root)
        print(f"  Task {task['number']}: {task['title']}" + (f" [{', '.join(marks)}]" if marks else ""))
        if files[task["number"]]:
            print(f"    files: {', '.join(files[task['number']])}")
    pairs = shared(files)
    print("shared files: " + ("; ".join(f"Task {a} and Task {b}: {', '.join(common)}" for a, b, common in pairs)
                              or "none"))
    return [task["number"] for task in found]


def _spec(lines, plan, root):
    value = spec(lines)
    if not value or value.lower() in NONE_WORDS:
        return "spec: none named, rulings stay provisional"
    places = [Path(value), root / value, plan.parent / value]
    return f"spec: {value} ({'found' if any(place.is_file() for place in places) else 'not found'})"


def _next(numbers, state):
    left = pending(numbers, state)
    if left:
        current = left[0]
        round_now = state["rounds"].get(current)
        loop = f", round {round_now} logged: next round if findings are open, else commit" if round_now else ""
        return f"next: Task {current}{loop}"
    if state["final"]:
        return "next: final review done, collect the rulings, delete the workspace, hand over to /finir"
    return "next: every task is complete, run the final review on the whole branch"


def _overview(root, source, ledger, entries):
    plan, lines = source
    state = parse(entries)
    name, default = branch(root), default_branch(root)
    print(f"workspace: {ledger.parent.as_posix()}")
    print(f"ledger: {ledger.as_posix()} ({len(entries)} lines)")
    print(f"repo: {root.as_posix()}, branch {name or 'detached'}, head {short(head(root))}")
    if name and name == default:
        print(f"warning: {name} is the default branch, branch off before the first task")
    if ensure_excluded(exclude_file(root)):
        print(f"{IGNORED} added to {exclude_file(root).as_posix()}")
    print(_spec(lines, plan, root))
    numbers = _tasks(lines, state, root)
    if not numbers:
        refuse(["no 'Task <N>' heading in the plan, it is not a writing-plans plan"])
    others = sorted(path for path in dirty(root) if not path.startswith(IGNORED))
    print(f"uncommitted paths: {len(others)}" + (f" ({', '.join(others[:8])})" if others else ""))
    print(_next(numbers, state))
    print(f"rulings so far: {len(state['rulings'])}")


def _note(ledger, text):
    problems = note_problems(text.strip())
    if problems:
        refuse(problems)
    with ledger.open("a", encoding=ENCODING, newline="\n") as handle:
        handle.write(text.strip() + "\n")
    print(f"noted: {text.strip()}")


def main():
    parser = argparse.ArgumentParser(description="Resolve the run's workspace and show where the plan stands.")
    parser.add_argument("plan")
    parser.add_argument("--note", help="append one line to the ledger")
    parser.add_argument("--rulings", action="store_true", help="print every Ruling line of the ledger, in order")
    args = parser.parse_args()
    plan, lines = _plan(args.plan)
    root = find_root(Path.cwd())
    ledger, entries = _ledger(folder_for(temp_root(), project_name(root), plan), plan)
    if args.note is not None:
        _note(ledger, args.note)
    elif args.rulings:
        print("\n".join(parse(entries)["rulings"]) or "no ruling")
    else:
        _overview(root, (plan, lines), ledger, entries)


if __name__ == "__main__":
    guard(main, "git status --short; git log --oneline -15; then read the plan and the ledger file by hand")
