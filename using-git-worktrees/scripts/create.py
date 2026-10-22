import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

import commands
import exclude
import gitinfo
import naming
import place
from common import FAILED, guard, refuse

TOOL = "using-git-worktrees"
PERMISSION = "permission"


def check(root, args, path):
    git_dir, common = gitinfo.git_dirs(root)
    problems = []
    if git_dir != common and not gitinfo.is_submodule(root):
        problems.append("this is already a linked worktree: do not create another")
    problems += naming.problems(args.branch, gitinfo.branch_names(root))
    problems += place.problems(path, root)
    if problems:
        refuse(problems)
    return common


def nested_folder(path, root):
    return path.resolve().parent.relative_to(root.resolve()).as_posix()


def patterns_for(path, root):
    found = list(exclude.LOCAL_PATTERNS)
    if place.is_nested(path, root) and not nested_folder(path, root).startswith(".ia"):
        found.append("/" + nested_folder(path, root) + "/")
    return found


def add(root, args, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    code, out, err = gitinfo.git(root, "worktree", "add", "--no-track", "-b", args.branch, str(path), args.base)
    if code != 0:
        print(f"{TOOL}: git worktree add failed: {(out + err).strip()}")
        if PERMISSION in err.lower():
            print("the sandbox blocked the worktree: work in place and say so")
        print(f"by hand: git worktree add --no-track -b {args.branch} \"{path.as_posix()}\" {args.base}")
        sys.exit(FAILED)


def main():
    parser = argparse.ArgumentParser(prog="create.py")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--base", default="HEAD")
    args = parser.parse_args()
    root = gitinfo.toplevel(Path.cwd())
    path = Path(args.path)
    common = check(root, args, path)
    added = exclude.ensure_excluded(common, patterns_for(path, root))
    add(root, args, path)
    print(f"worktree: {path.resolve().as_posix()}")
    print(f"branch: {args.branch} from {args.base}, no upstream")
    if added:
        print("added to .git/info/exclude: " + ", ".join(added))
    install = commands.install_command(path)
    print("install: " + (" ".join(install) if install else "nothing to install"))
    if place.is_nested(path, root):
        for hint in exclude.runner_hints(root, nested_folder(path, root)):
            print("runner: " + hint)


if __name__ == "__main__":
    guard(TOOL, main, "git worktree add --no-track -b <branch> <path> HEAD")
