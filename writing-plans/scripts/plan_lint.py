import sys

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from parse import split_tasks
from placement import check_location, excluded
from rules import check_header, check_task, check_text

TOOL = "plan_lint"
ENCODING = "utf-8"
FAILED, REFUSED = 1, 2


def problems_of(text):
    header, tasks = split_tasks(text)
    found = check_header(header) + check_text(text)
    if not tasks:
        found.append("no '### Task N: name' heading")
    for task in tasks:
        found += check_task(task)
    return found


def main():
    if len(sys.argv) != 2:
        print(f"{TOOL}: one argument, the plan file")
        print(f'by hand: python -I "{Path(__file__).as_posix()}" <repo>/.ia/plans/YYYY-MM-DD-<feature>.md')
        sys.exit(FAILED)
    path = Path(sys.argv[1])
    where, root = check_location(path)
    found = where + problems_of(path.read_text(encoding=ENCODING))
    if root is not None and not excluded(root):
        found.append(f".ia is not in {root.as_posix()}/.git/info/exclude: add the line .ia")
    for problem in found:
        print(f"refused: {problem}")
    if found:
        sys.exit(REFUSED)
    print(f"{TOOL}: ok")


try:
    main()
except SystemExit:
    raise
except Exception as error:
    print(f"{TOOL}: {type(error).__name__}: {error}")
    print(f'by hand: read {" ".join(sys.argv[1:])} against SKILL.md, section "Rules that never bend"')
    sys.exit(FAILED)
