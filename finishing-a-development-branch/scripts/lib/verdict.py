import re
from pathlib import PurePosixPath

KINDS = ("normal", "worktree", "detached")
BASE_NAMES = ("main", "master", "develop", "trunk")
OWNED_FOLDERS = ((".worktrees",), ("worktrees",), (".ia", "worktrees"))
ATTRIBUTION = re.compile(
    r"^(co-authored-by:.*(claude|anthropic|codex|copilot|cursor|gemini|jules|devin|aider|openai))"
    r"|^claude-|generated with|claude\.ai/code|claude\.com/claude-code|^made-with:|^agent-logs-url",
    re.IGNORECASE | re.MULTILINE)
TEST_MARKERS = {
    "package.json": "npm test",
    "Cargo.toml": "cargo test",
    "go.mod": "go test ./...",
    "pyproject.toml": "python -m pytest",
    "pytest.ini": "python -m pytest",
    "tox.ini": "python -m pytest",
    "build.gradle": "gradlew test",
    "build.gradle.kts": "gradlew test",
    "pom.xml": "mvn test",
    "Makefile": "make test",
}
TEMPLATES = (".github/pull_request_template.md", ".github/PULL_REQUEST_TEMPLATE.md", "pull_request_template.md",
             "PULL_REQUEST_TEMPLATE.md", "docs/pull_request_template.md", "docs/PULL_REQUEST_TEMPLATE.md")


def environment(git_dir, common_dir, branch):
    if git_dir == common_dir:
        return KINDS[0]
    return KINDS[1] if branch else KINDS[2]


def has_attribution(text):
    return bool(ATTRIBUTION.search(text))


def pick_base(counts):
    if not counts:
        return None, False
    best = min(counts.values())
    tied = sorted((name for name, count in counts.items() if count == best), key=_rank)
    return tied[0], len(tied) > 1 and not _preferred(tied)


def _rank(name):
    return BASE_NAMES.index(name) if name in BASE_NAMES else len(BASE_NAMES)


def _preferred(names):
    return names[0] in BASE_NAMES and (len(names) == 1 or names[1] not in BASE_NAMES)


def owned_worktree(path, main_root):
    try:
        relative = PurePosixPath(path).relative_to(PurePosixPath(main_root))
    except ValueError:
        return False
    return any(relative.parts[:len(folder)] == folder and len(relative.parts) > len(folder)
               for folder in OWNED_FOLDERS)


def removal(owned, landed, dirty, ia_files):
    if not owned:
        return False, "not created by using-git-worktrees: the host owns it, leave it"
    if not landed:
        return False, "work is neither merged into the base nor pushed"
    if dirty:
        return False, f"{dirty} uncommitted paths would be lost"
    if ia_files:
        return True, f"first copy {ia_files} files of its .ia/ into the main repository"
    return True, "work is landed and nothing is left inside"


def test_hints(names):
    found = [command for marker, command in TEST_MARKERS.items() if marker in names]
    found += ["python -m unittest discover"] if any(_python_test(name) for name in names) else []
    return list(dict.fromkeys(found))


def _python_test(name):
    return name.startswith("test_") and name.endswith(".py")


def find_template(names):
    lowered = {name.lower(): name for name in names}
    return next((lowered[path.lower()] for path in TEMPLATES if path.lower() in lowered), None)
