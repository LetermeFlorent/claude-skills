import fnmatch
import os
import re
from pathlib import PurePosixPath

from runs import git

RULE = 3
NUL = "\0"
NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "npm-debug.log", "yarn-error.log"}
PATTERNS = ("*.log", "*.bak", "*.old", "*.orig", "*.rej", "*.tmp", "*.swp", "*~", "*.pyc", "*.class", "*.o")
COPY = re.compile(r"( copy( \d+)?| - Copy( \(\d+\))?| \(\d+\))\.[^.]+$|\.copy\.[^.]+$", re.IGNORECASE)
BUILT = {"__pycache__", "node_modules", "dist", "build", ".pytest_cache", ".mypy_cache", "coverage", ".next"}


def junk(rel):
    path = PurePosixPath(rel)
    built = BUILT & set(path.parts[:-1])
    if built:
        return f"generated output in {sorted(built)[0]}/"
    if path.name in NAMES or any(fnmatch.fnmatch(path.name, pattern) for pattern in PATTERNS):
        return "leftover file"
    return "copy of another file" if COPY.search(path.name) else None


def scope_of(files):
    parents = [str(PurePosixPath(item["rel"]).parent) for item in files]
    return os.path.commonpath(parents).replace("\\", "/") or "." if parents else "."


def check(files, root, config):
    scope = scope_of(files)
    listed = git(root, "ls-files", "-z", "--", scope)
    tracked = listed is not None
    paths = listed.split(NUL)[:-1] if tracked else [item["rel"] for item in files]
    findings = []
    for rel in paths:
        why = junk(rel)
        if why:
            findings.append({"rule": RULE, "file": rel, "line": 0, "what": why,
                             "proof": "tracked by git" if tracked else "file name"})
    return findings, {}
