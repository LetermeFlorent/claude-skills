from pathlib import PurePosixPath

from common import SEPARATOR
from detect import TEST_DIRS, node_tool, package_manager, python_for, uses_xdist

PYTHON_ENV = {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
NODE_ENV = {"NO_COLOR": "1", "FORCE_COLOR": "0"}
SCRIPT_ENV = {**NODE_ENV, "CI": "true"}
RUST_SUFFIX, GO_SUFFIX, PYTHON_SUFFIX = ".rs", ".go", ".py"
RUST_TESTS = "tests"
CURRENT = "."


def split(target):
    path, _, name = (target or "").partition(SEPARATOR)
    return path.replace("\\", "/") or None, name or None


def is_dotted(target):
    return SEPARATOR not in target and "/" not in target and "\\" not in target and not target.endswith(PYTHON_SUFFIX)


def _pytest(root, target, workers):
    command = [python_for(root), "-m", "pytest", "-p", "no:cacheprovider"]
    command += ["-n", str(workers)] if uses_xdist(root) else []
    return command + ([target] if target else []), PYTHON_ENV


def _unittest(root, target, workers):
    command = [python_for(root), "-m", "unittest"]
    if target and is_dotted(target):
        return command + [target], PYTHON_ENV
    path, name = split(target)
    start = str(PurePosixPath(path).parent) if path else next((d for d in TEST_DIRS if (root / d).is_dir()), None)
    command += ["discover"] + (["-s", start] if start else [])
    command += ["-p", PurePosixPath(path).name] if path else []
    command += ["-k", "*." + name.replace(SEPARATOR, ".")] if name else []
    return command, PYTHON_ENV


def _node_target(target):
    path, name = split(target)
    return ([path] if path else []) + (["-t", name] if name else [])


def _jest(root, target, workers):
    return [node_tool(root, "jest"), "--watchAll=false", f"--maxWorkers={workers}", *_node_target(target)], NODE_ENV


def _vitest(root, target, workers):
    return [node_tool(root, "vitest"), "run", f"--maxWorkers={workers}", *_node_target(target)], NODE_ENV


def _script(root, target, workers):
    path, _ = split(target)
    return [package_manager(root), "test", *(["--", path] if path else [])], SCRIPT_ENV


def _cargo(root, target, workers):
    path, name = split(target)
    command = ["cargo", "test", "-j", str(workers)]
    is_file = bool(path) and path.endswith(RUST_SUFFIX)
    if is_file and PurePosixPath(path).parts[0] == RUST_TESTS:
        command += ["--test", PurePosixPath(path).stem]
    test_filter = name or (None if is_file else path)
    return command + ([test_filter] if test_filter else []) + ["--", f"--test-threads={workers}"], {}


def _go(root, target, workers):
    path, name = split(target)
    if not path:
        package = "./..."
    elif path.endswith(GO_SUFFIX):
        parent = str(PurePosixPath(path).parent)
        package = CURRENT if parent == CURRENT else f"./{parent}"
    else:
        package = path
    command = ["go", "test", "-v", "-p", str(workers), package]
    return command + (["-run", f"^{name}$"] if name else []), {}


BUILDERS = {"pytest": _pytest, "unittest": _unittest, "jest": _jest, "vitest": _vitest,
            "npm": _script, "cargo": _cargo, "go": _go}


def build(runner, root, target, workers):
    return BUILDERS[runner](root, target, workers)
