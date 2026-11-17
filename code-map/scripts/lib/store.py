import json
import os
from pathlib import Path

from common import refuse, run
from extract import extract

SKIP_DIRS = frozenset({".git", ".ia", "node_modules", "dist", "build", "target", "out", "bin", "obj", "venv",
                       ".venv", "__pycache__", "vendor", "coverage"})
INTERNAL_DIR = ".ia"
MAX_BYTES = 1024 * 1024
SNIFF_BYTES = 8192
NUL = "\0"
SEP = "/"
VERSION = 2
STORE_PARTS = (".ia", "code-map")
MAP_NAME = "map.json"
REPORT_NAME = "report.md"


def store_dir(root):
    return Path(root).joinpath(*STORE_PARTS)


def empty(scope=""):
    return {"version": VERSION, "scope": scope, "files": {}, "skipped": {}}


def load(root):
    try:
        data = json.loads((store_dir(root) / MAP_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return empty()
    return data if data.get("version") == VERSION else empty()


def save(root, data):
    folder = store_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    temp = folder / (MAP_NAME + ".tmp")
    temp.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    os.replace(temp, folder / MAP_NAME)


def unchanged(entry, sig):
    return bool(entry) and entry.get("sig") == sig


def refresh(root, scope=None):
    old = load(root)
    scope = old.get("scope", "") if scope is None else scope.strip("/")
    if scope != old.get("scope", ""):
        old = empty(scope)
    data = empty(scope)
    changed = 0
    for path in list_files(root):
        sig = signature(root, path) if in_scope(path, scope) else None
        if sig is None:
            continue
        if unchanged(old["files"].get(path), sig):
            data["files"][path] = old["files"][path]
        elif old["skipped"].get(path) == sig:
            data["skipped"][path] = sig
        else:
            changed += 1
            text = read_text(root, path)
            if text is None:
                data["skipped"][path] = sig
            else:
                data["files"][path] = {**extract(path, text), "sig": sig}
    if changed or data["files"].keys() != old["files"].keys():
        save(root, data)
    return data, changed


def git_files(root):
    code, out = run(["git", "ls-files", "-z", "-co", "--exclude-standard"], root)
    if code != 0:
        return None
    return [name for name in out.split(NUL) if name]


def walk_files(root):
    found = []
    for folder, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in names:
            found.append(os.path.relpath(os.path.join(folder, name), root).replace(os.sep, SEP))
    return found


def list_files(root):
    names = git_files(root)
    if names is None:
        names = walk_files(root)
    kept = {n.replace(os.sep, SEP) for n in names}
    return sorted(n for n in kept if n.split(SEP)[0] != INTERNAL_DIR)


def in_scope(path, scope):
    return not scope or path == scope or path.startswith(scope + SEP)


def find_root(given):
    if given:
        root = Path(given).resolve()
        if not root.is_dir():
            refuse([f"{given} is not a folder"])
        return root
    code, out = run(["git", "rev-parse", "--show-toplevel"], Path.cwd())
    return Path(out.strip()).resolve() if code == 0 and out.strip() else Path.cwd().resolve()


def signature(root, path):
    full = Path(root) / path
    try:
        info = os.stat(full)
    except OSError:
        return None
    if not full.is_file() or info.st_size > MAX_BYTES:
        return None
    return f"{info.st_size}:{info.st_mtime_ns}"


def read_text(root, path):
    try:
        with open(Path(root) / path, "rb") as handle:
            raw = handle.read()
    except OSError:
        return None
    if NUL.encode() in raw[:SNIFF_BYTES]:
        return None
    return raw.decode("utf-8", errors="replace")
