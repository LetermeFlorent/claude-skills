import json
import shutil

from common import DECODE_ERRORS, ENCODING

MANIFEST = "package.json"
LOCKS = (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun"), ("bun.lock", "bun"))
DEFAULT_MANAGER = "npm"
LINT, TYPECHECK = "lint", "typecheck"
LINT_SCRIPTS = (LINT,)
TYPE_SCRIPTS = (TYPECHECK, "type-check", "check-types", "tsc")
TSC = "tsc"
RUN = "run"
LOCAL_BIN = ("node_modules", ".bin")
BIN_SUFFIXES = ("", ".cmd")
NODE_SUFFIXES = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".css", ".scss")
PYTHON_SUFFIX = ".py"
RUFF = "ruff"
RUFF_FILES = ("ruff.toml", ".ruff.toml")
PYPROJECT = "pyproject.toml"
RUFF_SECTION = "[tool.ruff"
TSCONFIG = "tsconfig.json"


def _manager(root):
    return next((name for lock, name in LOCKS if (root / lock).exists()), DEFAULT_MANAGER)


def _scripts(root):
    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding=ENCODING, errors=DECODE_ERRORS))
    except (OSError, ValueError):
        return {}
    scripts = manifest.get("scripts")
    return scripts if isinstance(scripts, dict) else {}


def _has_bin(root, name):
    return any(root.joinpath(*LOCAL_BIN, name + suffix).exists() for suffix in BIN_SUFFIXES)


def _node(root, paths):
    if not (root / MANIFEST).exists() or not any(path.endswith(NODE_SUFFIXES) for path in paths):
        return []
    scripts, manager = _scripts(root), _manager(root)
    lint = next((name for name in LINT_SCRIPTS if name in scripts), None)
    typing = next((name for name in TYPE_SCRIPTS if name in scripts), None)
    found = [(LINT, [manager, RUN, lint])] if lint else []
    if typing:
        found.append((TYPECHECK, [manager, RUN, typing]))
    elif (root / TSCONFIG).exists() and _has_bin(root, TSC):
        found.append((TYPECHECK, [manager, "exec", TSC, "--noEmit", "--incremental", "false"]))
    return found


def _ruff_configured(root):
    if any((root / name).exists() for name in RUFF_FILES):
        return True
    pyproject = root / PYPROJECT
    return pyproject.exists() and RUFF_SECTION in pyproject.read_text(encoding=ENCODING, errors=DECODE_ERRORS)


def _python(root, paths):
    files = [path for path in paths if path.endswith(PYTHON_SUFFIX) and (root / path).exists()]
    if files and _ruff_configured(root) and shutil.which(RUFF):
        return [(LINT, [RUFF, "check", *files])]
    return []


def detect(root, paths):
    return _node(root, paths) + _python(root, paths)
