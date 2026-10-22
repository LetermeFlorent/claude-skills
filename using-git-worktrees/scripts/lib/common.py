import os
import shutil
import subprocess
import sys

ENCODING = "utf-8"
DECODE_ERRORS = "replace"
INTERRUPTED = 130
FAILED = 1
REFUSED = 2
LOW_PRIORITY = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
QUIET_ENV = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}


def guard(tool, main, hint):
    sys.stdout.reconfigure(encoding=ENCODING, errors=DECODE_ERRORS)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        print(f"{tool}: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(FAILED)


def run(command, cwd, timeout, env=None):
    program = shutil.which(command[0]) or command[0]
    try:
        done = subprocess.run([program, *command[1:]], cwd=str(cwd), capture_output=True, text=True,
                              timeout=timeout, encoding=ENCODING, errors=DECODE_ERRORS,
                              env={**os.environ, **QUIET_ENV, **(env or {})}, creationflags=LOW_PRIORITY)
    except FileNotFoundError:
        return None, "", f"{command[0]} is not installed"
    except subprocess.TimeoutExpired:
        return None, "", f"{command[0]} timed out after {timeout} s"
    return done.returncode, done.stdout, done.stderr


def refuse(problems):
    for problem in problems:
        print(f"refused: {problem}")
    sys.exit(REFUSED)
