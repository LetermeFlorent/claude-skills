import re
from pathlib import Path

from common import run

GIT_TIMEOUT = 60
GIT, REV_PARSE, LOG = "git", "rev-parse", "log"
ORIGIN = "origin"
UNTRACKED = "??"
DELETED = "D"
RENAMED = ("R", "C")
CODE_WIDTH = 2
SEPARATOR = "\0"
RECORD, FIELD = chr(0x1E), chr(0x1F)
GITHUB = re.compile(r"github\.com[:/](?P<owner>[^/]+)/")
PLAIN = re.compile(r"^(file://|ssh://|[\w.-]+@[\w.-]+:|[A-Za-z]:[\\/]|\.{0,2}/|\\\\)")
OPERATIONS = {"MERGE_HEAD": "merge", "rebase-merge": "rebase", "rebase-apply": "rebase", "CHERRY_PICK_HEAD":
              "cherry-pick", "REVERT_HEAD": "revert", "BISECT_LOG": "bisect"}
UNPUSHED = ("HEAD", "--not", "--remotes")
REMOTE_KINDS = ("none", "github", "plain", "other")
NO_REMOTE, GITHUB_KIND, PLAIN_KIND, OTHER_KIND = REMOTE_KINDS


def git(root, *args, stdin=None):
    return run([GIT, *args], root, GIT_TIMEOUT, stdin)


def read(root, *args):
    code, out, _ = git(root, *args)
    return out if code == 0 else None


def find_root(start):
    top = read(start, REV_PARSE, "--show-toplevel")
    if top is None:
        raise RuntimeError(f"{start} is not inside a git repository")
    return Path(top.strip()).resolve()


def changes(root):
    output = read(root, "status", "--porcelain=v1", "-z", "--untracked-files=all") or ""
    parts, entries = output.split(SEPARATOR), []
    while parts:
        item = parts.pop(0)
        if not item:
            continue
        code, path = item[:CODE_WIDTH], item[CODE_WIDTH + 1:]
        entry = {"code": code, "path": path, "new": code == UNTRACKED, "deleted": DELETED in code}
        if code[0] in RENAMED and parts:
            entry["from"] = parts.pop(0)
        entries.append(entry)
    return entries


def branch(root):
    name = (read(root, "branch", "--show-current") or "").strip()
    upstream = read(root, REV_PARSE, "--abbrev-ref", "--symbolic-full-name", "@{u}")
    return name, upstream.strip() if upstream else None


def remote(root):
    url = (read(root, "remote", "get-url", ORIGIN) or "").strip()
    found = GITHUB.search(url)
    if not url:
        return {"kind": NO_REMOTE, "url": url, "owner": None}
    if found:
        return {"kind": GITHUB_KIND, "url": url, "owner": found.group("owner")}
    return {"kind": PLAIN_KIND if PLAIN.match(url) else OTHER_KIND, "url": url, "owner": None}


def operation(root):
    git_dir = read(root, REV_PARSE, "--absolute-git-dir")
    folder = Path(git_dir.strip()) if git_dir else root / ".git"
    return next((name for marker, name in OPERATIONS.items() if (folder / marker).exists()), None)


def unpushed(root):
    output = read(root, "rev-list", *UNPUSHED) or ""
    return output.split()


def pushed_matching(root, pattern):
    log = read(root, LOG, "--remotes", f"--format=%h{FIELD}%B{RECORD}") or ""
    records = (record.strip().partition(FIELD) for record in log.split(RECORD))
    return [sha for sha, _, body in records if sha and pattern.search(body)]


def message(root, commit):
    return read(root, LOG, "-1", "--format=%B", commit) or ""
