import contextlib
import os
import re
import shutil
import sys
from pathlib import Path

from common import read_json, run

MEASURE = ("scripts", "measure.py")
SCAN = ("scripts", "scan.py")
SKILLS = "skills"
HOME_CONFIG = ".claude"
CONFIG_VARIABLE = "CLAUDE_CONFIG_DIR"
MEASURE_TIMEOUT = 600
SCAN_TIMEOUT = 120
TAIL = 400
RUN_LINE = re.compile(r"^run: (.+)$", re.MULTILINE)
FINDINGS = "findings.json"
RUNS = (".ia", "clean-code")


def candidates(name, given, skill):
    found = [Path(given)] if given else []
    found.append(skill.parent / name)
    config = os.environ.get(CONFIG_VARIABLE)
    if config:
        found.append(Path(config) / SKILLS / name)
    found.append(Path.home() / HOME_CONFIG / SKILLS / name)
    return found


def locate(name, given, skill, script):
    tried = candidates(name, given, skill)
    hit = next((folder.joinpath(*script) for folder in tried if folder.joinpath(*script).is_file()), None)
    return hit, [folder.as_posix() for folder in tried]


def _tail(out, err):
    return (out + err).strip()[-TAIL:] or "no output"


def _drop(root, folder):
    if folder.resolve().parent == root.joinpath(*RUNS).resolve():
        shutil.rmtree(folder, ignore_errors=True)
        for empty in (folder.parent, folder.parent.parent):
            with contextlib.suppress(OSError):
                empty.rmdir()


def measure(root, scope, script):
    code, out, err = run([sys.executable, "-I", str(script), str(scope)], root, MEASURE_TIMEOUT)
    found = RUN_LINE.search(out or "")
    if code != 0 or not found:
        return None, _tail(out, err)
    folder = Path(found.group(1).strip())
    try:
        return read_json(folder / FINDINGS)["findings"], None
    finally:
        _drop(root, folder)


def scan(root, paths, script):
    outputs, problems = [], []
    for path in paths:
        code, out, err = run([sys.executable, "-I", str(script), str(root / path), "--no-git"], root, SCAN_TIMEOUT)
        if code == 0:
            outputs.append(out)
        else:
            problems.append(f"{path}: {_tail(out, err)}")
    return "\n".join(outputs), problems
