from pathlib import Path

DEFAULT_FOLDER = (".ia", "worktrees")
TEMP_MARKERS = ("/appdata/local/temp", "/tmp/", "/temp/")


def posix(path):
    return Path(path).resolve().as_posix().lower() + "/"


def is_nested(path, root):
    return Path(path).resolve().is_relative_to(Path(root).resolve())


def choose(root, others, slug, named=None):
    if named:
        return Path(named).resolve() / slug, "the folder the user or the repository names"
    if others:
        first = Path(others[0]["path"])
        return first.parent / slug, "same folder as the existing worktree " + first.as_posix()
    return Path(root).joinpath(*DEFAULT_FOLDER) / slug, "default: inside the repository's .ia folder"


def problems(path, root):
    found = []
    resolved = Path(path).resolve()
    if not is_nested(path, root) and any(marker in posix(path) for marker in TEMP_MARKERS):
        found.append(f"{resolved.as_posix()} is in a temporary folder, which gets cleaned")
    if resolved.parent == Path.home().resolve():
        found.append(f"{resolved.as_posix()} sits directly in the home folder")
    if resolved.exists():
        found.append(f"{resolved.as_posix()} already exists")
    if resolved == Path(root).resolve():
        found.append("the worktree path is the repository itself")
    return found
