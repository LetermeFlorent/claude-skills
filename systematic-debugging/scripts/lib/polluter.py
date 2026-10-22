import fnmatch
import os
import shlex
from pathlib import Path

PLACEHOLDER = "{}"
ANY_DEPTH = "**/"
CURRENT = "./"
HALVES = 2
SKIPPED_FOLDERS = frozenset({".git", ".ia", ".venv", "venv", "node_modules", "target", "dist", "build",
                             "__pycache__"})


def clean_path(text):
    return Path(text).as_posix().removeprefix(CURRENT)


def matches(relative, pattern):
    return fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(relative, pattern.replace(ANY_DEPTH, ""))


def collect(root, pattern):
    pattern = clean_path(pattern)
    found = []
    for folder, subfolders, names in os.walk(root):
        subfolders[:] = sorted(name for name in subfolders if name not in SKIPPED_FOLDERS)
        for name in names:
            relative = Path(folder, name).relative_to(root).as_posix()
            if matches(relative, pattern):
                found.append(relative)
    return sorted(found)


def expand(template, files):
    words = shlex.split(template)
    if PLACEHOLDER not in words:
        return None
    at = words.index(PLACEHOLDER)
    return [*words[:at], *files, *words[at + 1:]]


def bisect(candidates, fails):
    suspects = list(candidates)
    while len(suspects) > 1:
        middle = len(suspects) // HALVES
        first, second = suspects[:middle], suspects[middle:]
        if fails(first):
            suspects = first
        elif fails(second):
            suspects = second
        else:
            return suspects, False
    return suspects, True
