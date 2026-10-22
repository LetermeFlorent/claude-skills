import re
import subprocess
from pathlib import Path

NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
IGNORED = ".ia"
TIMEOUT = 20


def _exclude_file(root):
    done = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-path", "info/exclude"],
                          capture_output=True, text=True, timeout=TIMEOUT)
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip() or "git rev-parse failed")
    path = Path(done.stdout.strip())
    return path if path.is_absolute() else root / path


def excluded(root):
    target = _exclude_file(root)
    if not target.is_file():
        return False
    lines = [line.strip().rstrip("/") for line in target.read_text(encoding="utf-8").splitlines()]
    return IGNORED in lines or "/" + IGNORED in lines


def check_location(path):
    parts = path.resolve().parts
    if len(parts) < 3 or parts[-2] != "plans" or parts[-3] != IGNORED:
        return [f"the plan lives in <repo>/{IGNORED}/plans/, not in {path.parent}"], None
    problems = [] if NAME.match(path.name) else [f"the name {path.name} is not YYYY-MM-DD-<feature>.md"]
    return problems, path.parents[2]
