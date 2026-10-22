from pathlib import Path

RUNNER_FILES = (
    ("vitest.config.*", "test.exclude"), ("vite.config.*", "test.exclude"), ("jest.config.*", "testPathIgnorePatterns"),
    ("tsconfig.json", "exclude"), ("eslint.config.*", "ignores"), (".eslintrc*", "ignorePatterns"),
    ("pytest.ini", "norecursedirs"), ("tox.ini", "norecursedirs"), ("pyproject.toml", "norecursedirs"),
)
LOCAL_PATTERNS = (".ia/",)


def ensure_excluded(common_dir, patterns):
    target = Path(common_dir) / "info" / "exclude"
    target.parent.mkdir(parents=True, exist_ok=True)
    current = target.read_text(encoding="utf-8").splitlines() if target.exists() else []
    missing = [pattern for pattern in patterns if pattern not in current]
    if missing:
        text = "\n".join(current + missing) + "\n"
        target.write_text(text, encoding="utf-8")
    return missing


def runner_hints(root, folder):
    hints = []
    for pattern, key in RUNNER_FILES:
        for found in sorted(Path(root).glob(pattern)):
            hints.append(f"{found.name}: add '{folder}/**' to {key}")
    return hints
