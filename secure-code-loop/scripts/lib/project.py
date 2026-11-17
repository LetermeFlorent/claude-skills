import hashlib
import os
import re
from pathlib import Path, PurePosixPath

from common import last_line, run

GIT_TIMEOUT = 120
STATUS_WIDTH = 3
COPIED_OR_RENAMED = frozenset("RC")
SKIPPED_DIRS = frozenset({".git", "node_modules", ".venv", "venv", "__pycache__", "target", "dist", "build", "vendor",
                          ".tox", ".next", ".scannerwork", ".pytest_cache", ".mypy_cache", ".ruff_cache"})
TEMPORARY = re.compile(r"secure_?loop[-_]?tmp", re.IGNORECASE)
TEST_FILE = re.compile(r"(^|/)(tests?|__tests__|specs?)/|(^|/)test_[^/]*\.py$|_test\.(py|go)$"
                       r"|\.(test|spec)\.[cm]?[jt]sx?$|\.spec\.luau?$|(^|/)[A-Z]\w*Tests?\.(java|kt|php|cs)$")
CODE_SUFFIXES = frozenset({".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".vue", ".svelte",
                           ".php", ".rs", ".go", ".java", ".kt", ".cs", ".rb", ".lua", ".luau", ".c", ".h", ".cc",
                           ".cpp", ".hpp", ".swift", ".sh", ".ps1", ".sql"})


def git(root, *args):
    return run(["git", "-c", "core.quotepath=off", *args], root, GIT_TIMEOUT)


def git_names(root, *args):
    code, out, err = git(root, *args)
    if code != 0:
        raise RuntimeError(f"git {args[0]} failed: {last_line(err)}")
    return [name for name in out.split("\0") if name]


def root_of(folder):
    folder = Path(folder).resolve()
    code, out, _ = git(folder, "rev-parse", "--show-toplevel")
    return (Path(out.strip()).resolve(), True) if code == 0 and out.strip() else (folder, False)


def head_of(root):
    code, out, _ = git(root, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
    return out.strip() if code == 0 else None


def commit_of(root, revision):
    code, out, _ = git(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
    return out.strip() if code == 0 else None


def walk(root):
    found = []
    for folder, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIPPED_DIRS]
        base = Path(folder).relative_to(root).as_posix()
        found += [name if base == "." else f"{base}/{name}" for name in names]
    return found


def files(root, is_git):
    if not is_git:
        return sorted(walk(root))
    names = git_names(root, "ls-files", "-z", "--cached") + [
        name for name in git_names(root, "ls-files", "-z", "--others", "--exclude-standard") if not skipped(name)]
    return sorted({name for name in names if (root / name).is_file()})


def ignored(root, is_git):
    if not is_git:
        return []
    return git_names(root, "ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--directory")


def skipped(name):
    return bool(SKIPPED_DIRS & set(PurePosixPath(name).parts))


def protected(name, prefixes):
    return covered(name, prefixes) or skipped(name)


def status(root):
    parts, entries = iter(git_names(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")), {}
    for entry in parts:
        code = entry[:STATUS_WIDTH - 1]
        entries[entry[STATUS_WIDTH:]] = code
        if COPIED_OR_RENAMED & set(code):
            next(parts, None)
    return entries


def digest(path):
    try:
        return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return None


def line_count(path):
    try:
        return len(Path(path).read_bytes().splitlines())
    except OSError:
        return 0


def is_test(name):
    return bool(TEST_FILE.search(name)) and not TEMPORARY.search(name)


def is_code(name):
    return PurePosixPath(name).suffix.lower() in CODE_SUFFIXES and not TEMPORARY.search(name)


def within(name, paths):
    return any(name == path or name.startswith(f"{path}/") for path in paths)


def covered(name, prefixes):
    return any(name == prefix.rstrip("/") or (prefix.endswith("/") and name.startswith(prefix)) for prefix in prefixes)


def changed_since(root, commit):
    return set(git_names(root, "diff", "--name-only", "-z", commit, "--")) | set(
        git_names(root, "ls-files", "-z", "--others", "--exclude-standard"))


def touched(root, start):
    if not start.get("head"):
        return set()
    dirty = start.get("dirty") or {}
    return {name for name in changed_since(root, start["head"])
            if name not in dirty or digest(root / name) != dirty[name]}


def scope_files(root, start, names):
    spec, present = start.get("scope") or {}, set(names)
    if spec.get("base"):
        chosen = changed_since(root, spec["base"])
    elif spec.get("paths"):
        chosen = {name for name in names if within(name, spec["paths"])}
    else:
        return present
    return (chosen | touched(root, start)) & present


def snapshot(root, is_git, names):
    dirty = status(root) if is_git else {}
    return {"head": head_of(root) if is_git else None, "files": names, "ignored": ignored(root, is_git),
            "dirty": {name: digest(root / name) for name in dirty},
            "tests": {name: digest(root / name) for name in names if is_test(name)},
            "lines": {name: line_count(root / name) for name in names if is_code(name)}}
