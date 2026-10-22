import datetime
import subprocess
from pathlib import Path

from common import DECODE_ERRORS, ENCODING, read_json

GIT_TIMEOUT = 60
TOOL_PARTS = (".ia", "clean-code")
IGNORED = ".ia/"
RUN_FORMAT = "%Y-%m-%d-%H%M%S"
FINDINGS = "findings.json"
MEASURE = "measure.json"
SCORE = "score.json"
PLAN = "plan.md"
REV_PARSE = "rev-parse"
DEFAULTS = {"max_lines": 150, "max_files": 8, "max_params": 4, "max_nesting": 3, "max_function_lines": 40,
            "max_image_kb": 200, "max_bytes_per_pixel": 0.5, "webp_quality": 80, "exclude": [], "public_api": [],
            "reader_threshold": 150, "readers": 4}
CONFIG_NAME = "config.json"


def git(root, *args):
    try:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=GIT_TIMEOUT,
                              encoding=ENCODING, errors=DECODE_ERRORS)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def project_root(scope):
    top = git(scope if scope.is_dir() else scope.parent, REV_PARSE, "--show-toplevel")
    return Path(top.strip()).resolve() if top else (scope if scope.is_dir() else scope.parent)


def tool_dir(root):
    folder = root.joinpath(*TOOL_PARTS)
    folder.mkdir(parents=True, exist_ok=True)
    git_dir = git(root, REV_PARSE, "--absolute-git-dir")
    if git_dir:
        exclude = Path(git_dir.strip()) / "info" / "exclude"
        exclude.parent.mkdir(parents=True, exist_ok=True)
        text = exclude.read_text(encoding=ENCODING, errors=DECODE_ERRORS) if exclude.exists() else ""
        if IGNORED not in text.split():
            joiner = "" if text.endswith("\n") or not text else "\n"
            exclude.write_text(text + joiner + IGNORED + "\n", encoding=ENCODING)
    return folder


def new_run(root, out=None):
    parent = Path(out).resolve() if out else tool_dir(root)
    run = parent / datetime.datetime.now().strftime(RUN_FORMAT)
    run.mkdir(parents=True, exist_ok=True)
    return run


def runs(root, out=None):
    folder = Path(out).resolve() if out else root.joinpath(*TOOL_PARTS)
    return sorted(p for p in folder.iterdir() if p.is_dir()) if folder.is_dir() else []


def latest_run(root, wanted=None):
    if wanted:
        run = Path(wanted).resolve()
        if not (run / FINDINGS).exists():
            raise FileNotFoundError(f"{run} holds no {FINDINGS}, pick a folder under {root.joinpath(*TOOL_PARTS)}")
        return run
    found = runs(root)
    if not found:
        raise FileNotFoundError(f"no audit under {root.joinpath(*TOOL_PARTS)}, run measure.py first")
    return found[-1]


def load_config(root):
    config = dict(DEFAULTS)
    path = root.joinpath(*TOOL_PARTS, CONFIG_NAME)
    if path.exists():
        try:
            config.update(read_json(path))
        except ValueError as error:
            print(f"warning: {path} unreadable ({error}), defaults used")
    return config
