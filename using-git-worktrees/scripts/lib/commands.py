import json
from pathlib import Path

LOCKS = (("pnpm-lock.yaml", ["pnpm", "install", "--frozen-lockfile", "--prefer-offline"]),
         ("package-lock.json", ["npm", "ci", "--prefer-offline", "--no-audit", "--no-fund"]),
         ("yarn.lock", ["yarn", "install", "--frozen-lockfile"]))
TARGET_VARIABLE = "CARGO_TARGET_DIR"
NODE_RUNNERS = ("vitest", "jest")
PYTHON_MARKERS = ("pytest.ini", "pyproject.toml", "tox.ini", "tests")
PYTEST_FILES = ("pytest.ini", "conftest.py")
PYTEST_DECLARED = ("pyproject.toml", "tox.ini", "setup.cfg", "requirements.txt", "requirements-dev.txt")
NODE_LISTS = (("vitest", ["list"]), ("jest", ["--listTests"]))
PYTEST_LIST = ["python", "-m", "pytest", "--collect-only", "-q"]
LOCAL_BIN = ("node_modules", ".bin")
BIN_SUFFIXES = ("", ".cmd")


def test_script(root):
    package = Path(root) / "package.json"
    return json.loads(package.read_text(encoding="utf-8")).get("scripts", {}).get("test")


def node_test(root, workers):
    script = test_script(root)
    if not script:
        return None
    manager = "pnpm" if (Path(root) / "pnpm-lock.yaml").exists() else "npm"
    flags = [f"--maxWorkers={workers}"] if any(name in script for name in NODE_RUNNERS) else []
    return [manager, "test", *(["--", *flags] if flags else [])]


def declares_pytest(root):
    if any((root / name).exists() for name in PYTEST_FILES):
        return True
    return any("pytest" in (root / name).read_text(encoding="utf-8", errors="replace")
               for name in PYTEST_DECLARED if (root / name).is_file())


def python_test(root):
    if declares_pytest(root):
        return ["python", "-m", "pytest", "-q"]
    return ["python", "-m", "unittest", "discover", "-s", "tests"] if (root / "tests").is_dir() else None


def test_command(root, workers):
    root = Path(root)
    if (root / "package.json").exists():
        return node_test(root, workers)
    if (root / "Cargo.toml").exists():
        return ["cargo", "test", "-j", str(workers), "--", f"--test-threads={workers}"]
    if (root / "go.mod").exists():
        return ["go", "test", "-p", str(workers), "./..."]
    if any((root / name).exists() for name in PYTHON_MARKERS):
        return python_test(root)
    return None


def install_command(root):
    root = Path(root)
    if not (root / "package.json").exists() or (root / "node_modules").exists():
        return None
    for lock, command in LOCKS:
        if (root / lock).exists():
            return command
    return None


def extra_env(main_root, heap):
    env = {"CI": "1", "NODE_OPTIONS": f"--max-old-space-size={heap}"}
    if (Path(main_root) / "Cargo.toml").exists():
        env[TARGET_VARIABLE] = (Path(main_root) / "target").as_posix()
    return env


def list_command(root):
    root = Path(root)
    if (root / "package.json").exists():
        script = test_script(root) or ""
        binaries = ((root.joinpath(*LOCAL_BIN, name), flags) for name, flags in NODE_LISTS if name in script)
        return next(([str(binary), *flags] for binary, flags in binaries
                     if any(binary.with_name(binary.name + suffix).exists() for suffix in BIN_SUFFIXES)), None)
    return PYTEST_LIST if declares_pytest(root) else None


def reads_worktree(output, worktree, main_root):
    text = output.replace("\\", "/").lower()
    worktree, main_root = Path(worktree).resolve(), Path(main_root).resolve()
    names = [worktree.as_posix().lower() + "/"]
    if worktree.is_relative_to(main_root):
        names.append(worktree.relative_to(main_root).as_posix().lower() + "/")
    return any(name in text for name in names)
