import argparse
import datetime
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import guard, refuse, short, write_text
from repo import diff, dirty, find_root, head, is_ancestor, must, project_name, snapshot
from space import (IGNORED, TASK_ID, folder_for, load_record, named, package_path, review_path,
                   save_record, task_paths, temp_root)

CONTEXT = "-U10"
LISTED = 8
FILES_HEADING = "## Files changed"


def _content(title, root, left, right):
    stat = diff(root, left, right, "--stat")
    return "\n".join([f"# Review package, {title}", "", FILES_HEADING, stat.rstrip(), "", "## Diff",
                      diff(root, left, right, CONTEXT).rstrip(), ""])


def _warnings(root, record, paths, fresh):
    before = set(record["dirty"])
    unclaimed = sorted(path for path in dirty(root) - before - set(paths) if not path.startswith(IGNORED))
    for path in unclaimed[:LISTED]:
        print(f"unclaimed: {path} changed during the task but is in no report")
    if len(unclaimed) > LISTED:
        print(f"unclaimed: {len(unclaimed) - LISTED} more, see git status")
    for path in sorted(before & set(fresh)):
        print(f"mixed: {path} was already changed before the task started, another session may own part of it")
    if head(root) != record["base"]:
        print(f"head moved: the task started at {short(record['base'])}, HEAD is now {short(head(root))}")


def _announce(out, notes):
    print(f"package: {out.as_posix()}")
    print(f"review notes: {notes.as_posix()}")


def _task(args, folder):
    record = load_record(folder, args.task)
    if record is None:
        refuse([f"no record for task {args.task}: run brief.py first"])
    root = Path(record["root"])
    paths, fresh, problems = task_paths(record, root, args.paths)
    if problems:
        refuse(problems)
    tree = snapshot(root, record["base"], paths, named(folder, args.task, ".index"))
    first = args.full or not record["snapshots"]
    left = record["base_tree"] if first else record["snapshots"][-1]["tree"]
    if tree == left:
        refuse([f"the listed paths hold no change since {'the task started' if first else 'the last package'}"])
    out = package_path(folder, args.task, left, tree)
    write_text(out, _content(f"task {args.task}: {short(left)}..{short(tree)}", root, left, tree))
    record["snapshots"].append({"tree": tree, "paths": paths,
                                "at": datetime.datetime.now().isoformat(timespec="seconds")})
    save_record(folder, args.task, record)
    _announce(out, review_path(folder, args.task, tree))
    print(f"round: {len(record['snapshots']) - 1} ({'full diff from the base' if first else 'fix diff only'})")
    print(f"paths: {', '.join(paths)}")
    _warnings(root, record, paths, fresh)


def _branch(args, folder, root):
    base = must(root, "rev-parse", "--verify", f"{args.branch}^{{commit}}").strip()
    tip = head(root)
    if not is_ancestor(root, base, tip):
        refuse([f"HEAD is not a descendant of {args.branch}"])
    commits = must(root, "log", "--oneline", f"{base}..{tip}").strip()
    if not commits:
        refuse([f"no commit between {args.branch} and HEAD"])
    out = folder / f"branch-{short(base)}..{short(tip)}.diff"
    text = _content(f"branch {short(base)}..{short(tip)}", root, base, tip)
    write_text(out, text.replace(FILES_HEADING, f"## Commits\n{commits}\n\n{FILES_HEADING}", 1))
    _announce(out, folder / f"branch-{short(tip)}-review.md")
    print(f"commits: {len(commits.splitlines())}")


def main():
    parser = argparse.ArgumentParser(description="Write the diff a reviewer reads, for one task or the branch.")
    parser.add_argument("plan")
    parser.add_argument("task", nargs="?", help="the id given to brief.py")
    parser.add_argument("--paths", nargs="+", default=[], help="every path the task created, edited or deleted")
    parser.add_argument("--full", action="store_true", help="diff from the task's base even after a fix round")
    parser.add_argument("--branch", help="base commit or branch for the whole-branch package")
    args = parser.parse_args()
    plan = Path(args.plan).resolve()
    if not plan.is_file():
        refuse([f"no plan file at {plan.as_posix()}"])
    root = find_root(Path.cwd())
    folder = folder_for(temp_root(), project_name(root), plan)
    folder.mkdir(parents=True, exist_ok=True)
    if args.branch:
        _branch(args, folder, root)
    elif args.task and TASK_ID.match(args.task) and args.paths:
        _task(args, folder)
    else:
        refuse(["give a task id and --paths, or --branch <base>"])


if __name__ == "__main__":
    guard(main, "git status --short, then git diff -U10 <base> -- <paths> into a file of the workspace")
