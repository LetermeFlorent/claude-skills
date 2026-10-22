import fnmatch
import os
import re
from pathlib import Path

from common import DECODE_ERRORS, ENCODING

MAX_BYTES = 2_000_000
SKIP_DIRS = {"node_modules", "build", "dist", "out", "target", "run", ".git", ".gradle", "generated", ".next",
             ".nuxt", ".svelte-kit", ".turbo", ".cache", "coverage", "vendor", "__pycache__", ".venv", "venv",
             "obj", "bin", ".claude", ".ia", ".idea", ".vscode", "old"}
TEST_DIRS = {"test", "tests", "__tests__", "spec", "specs", "e2e", "testing", "gametest"}
DATA_DIRS = {"fixtures", "fixture", "__snapshots__", "snapshots", "testdata", "test-data", "__fixtures__"}
LOCALE_DIRS = {"i18n", "locales", "locale", "lang", "langs", "translations", "l10n"}
LOCALE_SUFFIXES = {".json", ".po", ".yml", ".yaml", ".properties", ".arb"}
TEST_NAME = re.compile(r"(\.(test|spec)\.[a-z]+$)|(^test_.*\.py$)|(_test\.(py|go)$)|(Tests?\.(java|kt|cs)$)")
TEST_MARKER = re.compile(r"^\s*(async\s+)?def test_|\b(it|test|describe)\s*\(|@Test\b|#\[test\]|^func Test|"
                         r"\bunittest\b|\bpytest\b", re.MULTILINE)
LANG_CODE = re.compile(r"^[a-z]{2}([_-][a-zA-Z]{2})?$")
MINIFIED = (".min.js", ".min.css", ".map")
SNAPSHOT = ".snap"
GETTEXT = ".po"


def relative(path, root):
    return path.relative_to(root).as_posix()


def excluded(rel, config):
    return any(fnmatch.fnmatch(rel, pattern) or rel.startswith(pattern.rstrip("/") + "/")
               for pattern in config["exclude"])


def walk(scope, root, config):
    if scope.is_file():
        yield scope
        return
    for folder, dirs, names in os.walk(scope):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")
                         and not excluded(relative(Path(folder, d), root), config))
        for name in sorted(names):
            path = Path(folder, name)
            if not excluded(relative(path, root), config) and not name.endswith(MINIFIED):
                yield path


def is_test(path, root, lines):
    parts = {part.lower() for part in path.relative_to(root).parts[:-1]}
    named = TEST_NAME.search(path.name) and any(TEST_MARKER.search(line) for line in lines)
    return bool(parts & TEST_DIRS) or bool(named)


def is_data(path, root):
    parts = {part.lower() for part in path.relative_to(root).parts[:-1]}
    return bool(parts & DATA_DIRS) or path.suffix == SNAPSHOT


def is_locale(path, root):
    if path.suffix.lower() not in LOCALE_SUFFIXES:
        return False
    parts = {part.lower() for part in path.relative_to(root).parts[:-1]}
    return bool(parts & LOCALE_DIRS) or bool(LANG_CODE.match(path.stem)) or path.suffix == GETTEXT


def read_lines(path):
    try:
        if path.stat().st_size > MAX_BYTES:
            return []
        return path.read_text(encoding=ENCODING, errors=DECODE_ERRORS).splitlines()
    except OSError:
        return []
