import re
from pathlib import Path

from common import run

GIT_TIMEOUT = 60
GITHUB = re.compile(r"github\.com[:/](?P<owner>[^/]+)/")
SKIPPED_REFS = ("HEAD",)


def git(cwd, *args):
    return run(["git", *args], cwd, GIT_TIMEOUT)


def read(cwd, *args):
    code, out, _ = git(cwd, *args)
    return out.strip() if code == 0 else None


def toplevel(start):
    top = read(start, "rev-parse", "--show-toplevel")
    if not top:
        raise RuntimeError(f"{start} is not inside a git repository")
    return Path(top).resolve()


def git_dirs(root):
    out = read(root, "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir") or ""
    lines = out.splitlines()
    return [Path(line).resolve() for line in lines[:2]] if len(lines) >= 2 else [None, None]


def is_submodule(root):
    return bool(read(root, "rev-parse", "--show-superproject-working-tree"))


def linked_worktrees(root):
    out = read(root, "worktree", "list", "--porcelain") or ""
    found = []
    for block in out.split("\n\n"):
        fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
        if "worktree" in fields:
            found.append({"path": Path(fields["worktree"]).resolve(), "branch": fields.get("branch", "")})
    return found


def branch_names(root):
    out = read(root, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes") or ""
    return [name for name in out.splitlines() if name.split("/")[-1] not in SKIPPED_REFS]


def remote_owner(root):
    url = read(root, "remote", "get-url", "origin") or ""
    match = GITHUB.search(url)
    return (match.group("owner") if match else ""), url


def dirty_count(root):
    return len((read(root, "status", "--porcelain") or "").splitlines())
