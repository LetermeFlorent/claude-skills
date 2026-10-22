import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = "brainstorming"
ENCODING = "utf-8"
DECODE_ERRORS = "replace"
INTERRUPTED = 130
FAILED = 1
REFUSED = 2
GIT_TIMEOUT = 30
LOW_PRIORITY = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
QUIET_ENV = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
TEMP_FOLDER = "claude-skills"
COMPANION_FOLDER = "concevoir"
HOST = "127.0.0.1"
WINDOWS = os.name == "nt"


def address(port, route):
    return f"http://{HOST}:{port}{route}"


def temp_root():
    return Path(tempfile.gettempdir()) / TEMP_FOLDER


def companion_root():
    return temp_root() / COMPANION_FOLDER


def guard(main, hint):
    sys.stdout.reconfigure(encoding=ENCODING, errors=DECODE_ERRORS)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except SystemExit:
        raise
    except Exception as error:
        print(f"{TOOL}: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(FAILED)


def refuse(problems):
    for problem in problems:
        print(f"refused: {problem}")
    sys.exit(REFUSED)


def run(command, cwd):
    program = shutil.which(command[0]) or command[0]
    try:
        done = subprocess.run([program, *command[1:]], cwd=str(cwd), capture_output=True, text=True,
                              timeout=GIT_TIMEOUT, encoding=ENCODING, errors=DECODE_ERRORS,
                              env={**os.environ, **QUIET_ENV}, creationflags=LOW_PRIORITY)
    except FileNotFoundError:
        return None, "", f"{command[0]} is not installed"
    except subprocess.TimeoutExpired:
        return None, "", f"{command[0]} timed out after {GIT_TIMEOUT} s"
    return done.returncode, done.stdout, done.stderr


def write_json(path, data):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding=ENCODING)
    os.replace(temporary, path)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding=ENCODING))
    except (OSError, ValueError):
        return None
