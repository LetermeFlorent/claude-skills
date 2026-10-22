import re
from pathlib import Path

from common import run

GIT_TIMEOUT = 120
GIT, REV_PARSE = "git", "rev-parse"
NO_QUOTING = ("-c", "core.quotePath=false")
SEPARATOR = "\0"
CODE_WIDTH = 2
RENAMED = ("R", "C")
DEFAULT_NAMES = ("main", "master")
GIT_DIR = ".git"
UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def git(root, *args, index=None):
    extra = {"GIT_INDEX_FILE": str(index)} if index else None
    return run([GIT, *NO_QUOTING, *args], root, GIT_TIMEOUT, extra)


def read(root, *args):
    code, out, _ = git(root, *args)
    return out if code == 0 else None


def must(root, *args, index=None):
    code, out, err = git(root, *args, index=index)
    if code != 0:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {(err or out).strip()}")
    return out


def find_root(start):
    top = read(start, REV_PARSE, "--show-toplevel")
    if top is None:
        raise RuntimeError(f"{start} is not inside a git repository")
    return Path(top.strip()).resolve()


def head(root):
    return must(root, REV_PARSE, "HEAD").strip()


def tree_of(root, rev):
    return must(root, REV_PARSE, f"{rev}^{{tree}}").strip()


def porcelain_paths(output):
    parts, found = output.split(SEPARATOR), set()
    while parts:
        item = parts.pop(0)
        if not item:
            continue
        found.add(item[CODE_WIDTH + 1:])
        if item[0] in RENAMED and parts:
            found.add(parts.pop(0))
    return found


def dirty(root):
    return porcelain_paths(read(root, "status", "--porcelain=v1", "-z", "--untracked-files=all") or "")


def in_tree(root, rev, path):
    return git(root, "cat-file", "-e", f"{rev}:{path}")[0] == 0


def snapshot(root, base, paths, index):
    must(root, "read-tree", base, index=index)
    must(root, "add", "-A", "--", *paths, index=index)
    return must(root, "write-tree", index=index).strip()


def diff(root, left, right, *options):
    return must(root, "diff", "--no-color", "--no-ext-diff", *options, left, right)


def is_ancestor(root, older, newer):
    return git(root, "merge-base", "--is-ancestor", older, newer)[0] == 0


def project_name(root):
    common = Path(must(root, REV_PARSE, "--git-common-dir").strip())
    folder = (common if common.is_absolute() else root / common).resolve()
    name = folder.parent.name if folder.name == GIT_DIR else folder.stem
    return UNSAFE.sub("-", name).strip("-") or "repo"


def exclude_file(root):
    found = Path(must(root, REV_PARSE, "--git-path", "info/exclude").strip())
    return found if found.is_absolute() else root / found


def branch(root):
    return (read(root, "branch", "--show-current") or "").strip()


def default_branch(root):
    remote_head = read(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if remote_head:
        return remote_head.strip().split("/", 1)[-1]
    local = (read(root, "branch", "--format=%(refname:short)") or "").split()
    return next((name for name in DEFAULT_NAMES if name in local), None)
