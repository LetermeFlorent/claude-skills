from pathlib import Path

from common import run

GIT = "git"
GIT_TIMEOUT = 60
FIELD, RECORD = chr(0x1F), chr(0x1E)
OPERATIONS = {"MERGE_HEAD": "merge", "rebase-merge": "rebase", "rebase-apply": "rebase", "CHERRY_PICK_HEAD":
              "cherry-pick", "REVERT_HEAD": "revert", "BISECT_LOG": "bisect"}
SKIPPED_FOLDERS = (".git", "node_modules", "target", "dist", "build", "__pycache__")


def read(root, *args):
    code, out, _ = run([GIT, *args], root, GIT_TIMEOUT)
    return out if code == 0 else None


def find_root(start):
    top = read(start, "rev-parse", "--show-toplevel")
    if top is None:
        raise RuntimeError(f"{start} is not inside a git repository")
    return Path(top.strip()).resolve()


def directories(root):
    git_dir = (read(root, "rev-parse", "--absolute-git-dir") or "").strip()
    common = (read(root, "rev-parse", "--path-format=absolute", "--git-common-dir") or "").strip()
    return Path(git_dir).resolve(), Path(common).resolve()


def branch_name(root):
    return (read(root, "branch", "--show-current") or "").strip()


def upstream(root):
    found = read(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    return found.strip() if found else None


def local_branches(root):
    return (read(root, "for-each-ref", "--format=%(refname:short)", "refs/heads") or "").split()


def ahead(root, base):
    count = read(root, "rev-list", "--count", f"{base}..HEAD")
    return int(count) if count and count.strip().isdigit() else None


def commits(root, base):
    log = read(root, "log", "--format=%h %s", f"{base}..HEAD") or ""
    return log.splitlines()


def bodies(root, base):
    log = read(root, "log", f"--format=%h{FIELD}%B{RECORD}", f"{base}..HEAD") or ""
    parts = (record.strip().partition(FIELD) for record in log.split(RECORD))
    return [(sha, body) for sha, _, body in parts if sha]


def dirty(root):
    return (read(root, "status", "--porcelain=v1", "--untracked-files=all") or "").splitlines()


def is_ancestor(root, older, newer):
    code, _, _ = run([GIT, "merge-base", "--is-ancestor", older, newer], root, GIT_TIMEOUT)
    return code == 0


def on_remote(root):
    found = read(root, "branch", "-r", "--contains", "HEAD") or ""
    return [line.strip() for line in found.splitlines() if "->" not in line]


def remote_url(root):
    return (read(root, "remote", "get-url", "origin") or "").strip()


def tracked_names(root):
    return set((read(root, "ls-files") or "").splitlines())


def operation(root):
    git_dir, _ = directories(root)
    return next((name for marker, name in OPERATIONS.items() if (git_dir / marker).exists()), None)


def folder_files(folder):
    if not folder.is_dir():
        return 0
    return sum(1 for item in folder.rglob("*") if item.is_file() and not set(item.parts) & set(SKIPPED_FOLDERS))
