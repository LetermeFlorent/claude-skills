import os
from pathlib import Path, PurePosixPath

from common import MANIFEST, read_lines
from project import TEMPORARY, digest, files, git, protected

PROBLEMS = ("changed test:", "missing test:", "left:")
BYTECODE = "__pycache__"


def inside(root, entry):
    path = Path(entry.replace("\\", "/"))
    path = Path(os.path.normpath(path if path.is_absolute() else root / path))
    try:
        name = path.relative_to(root).as_posix()
    except ValueError:
        return None
    return None if name in ("", ".") else name


def refusal(name, start):
    if name is None:
        return "outside the project"
    if name in start["files"]:
        return "existed at start"
    if protected(name, start.get("ignored") or []):
        return "ignored or tool folder at start"
    return None


def prune(root, name, held):
    for parent in PurePosixPath(name).parents:
        folder = root / parent
        if parent.as_posix() in held or folder == root or any(folder.iterdir()):
            return
        folder.rmdir()


def delete_listed(root, start, entries):
    held, lines = {parent.as_posix() for name in start["files"] for parent in PurePosixPath(name).parents}, []
    for entry in entries:
        name = inside(root, entry)
        why = refusal(name, start)
        if why is None and (root / name).is_dir():
            why = "a folder: list its files"
        if why:
            lines.append(f"kept: {entry} ({why})")
        elif (root / name).is_file():
            (root / name).unlink()
            for cached in (root / name).parent.glob(f"{BYTECODE}/{PurePosixPath(name).stem}.*.pyc"):
                cached.unlink()
                prune(root, cached.relative_to(root).as_posix(), held)
            prune(root, name, held)
            lines.append(f"deleted: {name}")
    return lines


def test_changes(root, start):
    changed, missing = [], []
    for name, before in (start.get("tests") or {}).items():
        now = digest(root / name)
        if now is None:
            missing.append(name)
        elif now != before:
            changed.append(name)
    return changed, missing


def restored(root, start, name):
    if not start.get("head") or name in (start.get("dirty") or {}):
        return False
    code, _, _ = git(root, "restore", f"--source={start['head']}", "--staged", "--worktree", "--", name)
    return code == 0


def restore(root, start):
    changed, missing = test_changes(root, start)
    tests = start.get("tests") or {}
    gone = [name for name in start["files"] if name not in tests and not (root / name).exists()]
    lines = []
    for name in sorted({*changed, *missing, *gone}):
        if restored(root, start, name):
            lines.append(f"restored: {name}")
        else:
            label = "changed test" if name in changed else "missing test" if name in missing else "gone"
            lines.append(f"{label}: {name}")
    return lines


def leftovers(root, start, is_git):
    before = set(start["files"])
    fresh = [name for name in files(root, is_git) if name not in before]
    return [f"left: {name}" if TEMPORARY.search(name) else f"new since start: {name}" for name in fresh]


def clean(root, start, work):
    lines = delete_listed(root, start, read_lines(work / MANIFEST))
    return lines + restore(root, start) + leftovers(root, start, start["is_git"])


def problems(lines):
    return [line for line in lines if line.startswith(PROBLEMS)]
