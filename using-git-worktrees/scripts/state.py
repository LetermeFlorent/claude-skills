import argparse
import os
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

import exclude
import gitinfo
import naming
import place
from common import guard

TOOL = "using-git-worktrees"
ACCOUNTS_VAR = "CLAUDE_SKILLS_ACCOUNTS"
TOKEN_HELPER = r'credential.helper=!f() { echo username=x-access-token; echo password=\$GH_TOKEN; }; f'


def isolation(root):
    git_dir, common = gitinfo.git_dirs(root)
    linked = git_dir != common and not gitinfo.is_submodule(root)
    return linked, (common.parent if common else root)


def fetch_lines(root, owner, value):
    tool = Path(value).expanduser() if value else None
    if not tool or not tool.exists():
        why = f"{ACCOUNTS_VAR} is not set" if not tool else f"{tool.as_posix()} does not exist"
        return [f"remote: github {owner}. No accounts tool ({why}): never a bare fetch, ask the user before any fetch"]
    return [f"remote: github {owner}. Fetch only when the base must be fresh, through the accounts tool:",
            f'  sh "{tool.as_posix()}" run github {owner} --cwd "{root.as_posix()}" -- git -c credential.helper= '
            f'-c "{TOKEN_HELPER}" fetch origin']


def report_remote(root):
    owner, url = gitinfo.remote_owner(root)
    if not url:
        print("remote: none, nothing to fetch")
    elif owner:
        print("\n".join(fetch_lines(root, owner, os.environ.get(ACCOUNTS_VAR))))
    else:
        print(f"remote: {url} (not GitHub, nothing is fetched here)")


def report_place(root, task, named):
    prefix = naming.convention(gitinfo.branch_names(root))
    print(f"branch convention: {prefix + '<slug>' if prefix else 'none found, plain slug'}")
    slug = naming.slugify(task) or "<slug>"
    path, why = place.choose(root, gitinfo.linked_worktrees(root)[1:], slug, named)
    print(f"proposed branch: {prefix}{slug}")
    print(f"proposed path: {path.as_posix()} ({why})")
    for problem in place.problems(path, root):
        print(f"problem: {problem}")
    if place.is_nested(path, root):
        folder = path.parent.resolve().relative_to(root.resolve()).as_posix()
        print(f"inside the repository: .ia/ is excluded by create.py; runners that would read {folder}/:")
        for hint in exclude.runner_hints(root, folder) or ["no runner config found"]:
            print("  " + hint)


def main():
    parser = argparse.ArgumentParser(prog="state.py")
    parser.add_argument("--task", default="")
    parser.add_argument("--folder", default="")
    args = parser.parse_args()
    task = args.task
    root = gitinfo.toplevel(Path.cwd())
    linked, main_root = isolation(root)
    print(f"repo: {root.as_posix()}")
    print(f"branch: {gitinfo.read(root, 'branch', '--show-current') or 'detached HEAD'}")
    if linked:
        print(f"already isolated: linked worktree of {main_root.as_posix()}. Skip creation")
        return
    print(f"isolated: no, main checkout (submodule: {'yes' if gitinfo.is_submodule(root) else 'no'})")
    print(f"uncommitted changes that stay here: {gitinfo.dirty_count(root)}")
    others = gitinfo.linked_worktrees(root)[1:]
    print("worktrees: " + (", ".join(w["path"].as_posix() for w in others) or "none"))
    report_remote(root)
    report_place(root, task, args.folder)


if __name__ == "__main__":
    guard(TOOL, main, "git worktree list; git branch -a; git status --short")
