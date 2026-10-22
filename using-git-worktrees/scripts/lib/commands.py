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


def node_test(root, workers):
    package = Path(root) / "package.json"
    script = json.loads(package.read_text(encoding="utf-8")).get("scripts", {}).get("test")
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
