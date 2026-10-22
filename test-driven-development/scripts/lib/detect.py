import json
import os
import re
import sys
from itertools import islice
from pathlib import Path

from common import DECODE_ERRORS, ENCODING, SEPARATOR

MARKERS = (".git", "pyproject.toml", "setup.py", "package.json", "Cargo.toml", "go.mod")
PYTEST_FILES = ("pytest.ini", "conftest.py")
PYTEST_SECTIONS = (("pyproject.toml", "[tool.pytest"), ("setup.cfg", "[tool:pytest]"), ("tox.ini", "[pytest]"))
PYTEST_IMPORT = re.compile(r"^\s*(import|from) pytest\b", re.M)
XDIST = re.compile(r"(?<![\w-])-n(?=[\s\"'=\d,\]]|$)|--numprocesses", re.M)
PYTHON_FILES = ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt")
TEST_DIRS = ("tests", "test")
TEST_PATTERN = "test_*.py"
SCAN_LIMIT = 40
SCAN_BYTES = 4000
MANIFEST = "package.json"
NODE_RUNNERS = ("vitest", "jest")
LOCKS = (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun"), ("bun.lock", "bun"))
DEFAULT_MANAGER = "npm"
LOCAL_BIN = ("node_modules", ".bin")
WINDOWS_SUFFIX = ".cmd"
VENVS = (".venv", "venv")
VENV_PYTHON = (("Scripts", "python.exe"), ("bin", "python"))
SUFFIX_FAMILY = {".py": "python", ".rs": "cargo", ".go": "go"}
NODE_SUFFIXES = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts", ".vue", ".svelte")
FAMILY_ORDER = ("python", "node", "cargo", "go")


def find_root(start):
    for folder in (start, *start.parents):
        if any((folder / marker).exists() for marker in MARKERS):
            return folder
    return start


def _read(path, limit=None):
    try:
        with open(path, encoding=ENCODING, errors=DECODE_ERRORS) as handle:
            return handle.read(limit) if limit else handle.read()
    except OSError:
        return ""


def pytest_config(root):
    return "\n".join(_read(root / name) for name, section in PYTEST_SECTIONS if section in _read(root / name))


def uses_xdist(root):
    return bool(XDIST.search(pytest_config(root) + _read(root / "pytest.ini")))


def _test_files(root):
    found = (root.glob(f"{folder}/**/{TEST_PATTERN}") for folder in TEST_DIRS if (root / folder).is_dir())
    return [*islice((path for group in found for path in group), SCAN_LIMIT), *root.glob(TEST_PATTERN)]


def _python(root):
    files = _test_files(root)
    if any((root / name).exists() for name in PYTEST_FILES) or pytest_config(root):
        return "pytest"
    if any(PYTEST_IMPORT.search(_read(path, SCAN_BYTES)) for path in files):
        return "pytest"
    return "unittest" if files or any((root / name).exists() for name in PYTHON_FILES) else None


def manifest(root):
    try:
        data = json.loads(_read(root / MANIFEST) or "null")
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def _node(root):
    data = manifest(root)
    if data is None:
        return None
    script = str((data.get("scripts") or {}).get("test", ""))
    packages = {**(data.get("dependencies") or {}), **(data.get("devDependencies") or {})}
    named = next((name for name in NODE_RUNNERS if name in script), None)
    listed = next((name for name in NODE_RUNNERS if name in packages), None)
    return named or (None if script else listed) or ("npm" if script else None)


def _cargo(root):
    return "cargo" if (root / "Cargo.toml").exists() else None


def _go(root):
    return "go" if (root / "go.mod").exists() else None


FAMILIES = {"python": _python, "node": _node, "cargo": _cargo, "go": _go}


def _family(target):
    suffix = Path(target.partition(SEPARATOR)[0]).suffix if target else ""
    return "node" if suffix in NODE_SUFFIXES else SUFFIX_FAMILY.get(suffix)


def runners(root, target):
    first = _family(target)
    order = ([first] if first else []) + [name for name in FAMILY_ORDER if name != first]
    return [runner for runner in (FAMILIES[name](root) for name in order) if runner]


def python_for(root):
    for venv in VENVS:
        for folder, name in VENV_PYTHON:
            candidate = root / venv / folder / name
            if candidate.exists():
                return str(candidate)
    return sys.executable


def node_tool(root, name):
    suffix = WINDOWS_SUFFIX if os.name == "nt" else ""
    candidate = root.joinpath(*LOCAL_BIN, name + suffix)
    if not candidate.exists():
        raise LookupError(f"{name} is not in node_modules/.bin: install the project's dependencies, then run again")
    return str(candidate)


def package_manager(root):
    return next((name for lock, name in LOCKS if (root / lock).exists()), DEFAULT_MANAGER)
