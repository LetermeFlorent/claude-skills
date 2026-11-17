import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = "secure-code-loop"
ENCODING = "utf-8"
DECODE_ERRORS = "replace"
FAILED, REFUSED, INTERRUPTED = 1, 2, 130
LOW_PRIORITY = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
QUIET_ENV = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
WORK_PARENT = "claude-skills"
WORK_PREFIX = "secure-code-loop-"
START_FILE = "start.json"
MANIFEST = "manifest.txt"
FALSE_POSITIVES = "false-positives.txt"
ADVISORIES = "advisories.txt"
HISTORY_FILE = "history.json"
FINDINGS_FILE = "findings.json"
LEDGERS = (MANIFEST, FALSE_POSITIVES, ADVISORIES)


def guard(main, hint):
    sys.stdout.reconfigure(encoding=ENCODING, errors=DECODE_ERRORS)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        print(f"{TOOL}: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(FAILED)


def refuse(reasons):
    for reason in reasons:
        print(f"refused: {reason}")
    sys.exit(REFUSED)


def run(command, cwd, timeout, env=None):
    program = shutil.which(command[0]) or command[0]
    try:
        done = subprocess.run([program, *command[1:]], cwd=str(cwd), capture_output=True, text=True,
                              encoding=ENCODING, errors=DECODE_ERRORS, timeout=timeout, stdin=subprocess.DEVNULL,
                              env={**os.environ, **QUIET_ENV, **(env or {})}, creationflags=LOW_PRIORITY)
    except FileNotFoundError:
        return None, "", f"{command[0]} is not installed"
    except subprocess.TimeoutExpired:
        return None, "", f"timed out after {timeout} s"
    return done.returncode, done.stdout, done.stderr


def last_line(text):
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return lines[-1] if lines else "no output"


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding=ENCODING))
    except (OSError, ValueError):
        return None


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding=ENCODING)


def read_lines(path):
    try:
        text = Path(path).read_text(encoding=ENCODING)
    except OSError:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def work_folder(text):
    work = Path(text).resolve()
    parent = (Path(tempfile.gettempdir()) / WORK_PARENT).resolve()
    found = work.parent == parent and work.name.startswith(WORK_PREFIX) and (work / START_FILE).is_file()
    return work if found else None


def new_work():
    parent = Path(tempfile.gettempdir()) / WORK_PARENT
    parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=WORK_PREFIX, dir=parent))
    for name in LEDGERS:
        (work / name).write_text("", encoding=ENCODING)
    return work
