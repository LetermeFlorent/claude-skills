import json
import os
import shutil
import subprocess
import sys

TOOL = "subagent-driven-development"
ENCODING = "utf-8"
DECODE_ERRORS = "replace"
INTERRUPTED = 130
FAILED = 1
REFUSED = 2
LOW_PRIORITY = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
QUIET_ENV = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
SHORT = 7
JSON_INDENT = 2


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


def run(command, cwd, timeout, extra_env=None):
    program = shutil.which(command[0]) or command[0]
    env = {**os.environ, **QUIET_ENV, **(extra_env or {})}
    try:
        done = subprocess.run([program, *command[1:]], cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
                              encoding=ENCODING, errors=DECODE_ERRORS, env=env, creationflags=LOW_PRIORITY)
    except FileNotFoundError:
        return None, "", f"{command[0]} is not installed"
    except subprocess.TimeoutExpired:
        return None, "", f"{command[0]} timed out after {timeout} s"
    return done.returncode, done.stdout, done.stderr


def refuse(problems):
    for problem in problems:
        print(f"refused: {problem}")
    sys.exit(REFUSED)


def read_json(path):
    return json.loads(path.read_text(encoding=ENCODING))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=JSON_INDENT, ensure_ascii=False), encoding=ENCODING)


def write_text(path, text):
    path.write_text(text, encoding=ENCODING, newline="\n")


def short(sha):
    return (sha or "")[:SHORT]
