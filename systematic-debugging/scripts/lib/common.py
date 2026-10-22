import shutil
import subprocess
import sys

TOOL = "find_polluter"
ENCODING = "utf-8"
DECODE_ERRORS = "replace"
FAILED = 1
REFUSED = 2
INTERRUPTED = 130
LOW_PRIORITY = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)


class ToolError(Exception):
    pass


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


def refuse(problems):
    for problem in problems:
        print(f"refused: {problem}")
    sys.exit(REFUSED)


def run(argv, cwd, timeout):
    program = shutil.which(argv[0]) or argv[0]
    try:
        done = subprocess.run([program, *argv[1:]], cwd=str(cwd), stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout,
                              creationflags=LOW_PRIORITY)
    except FileNotFoundError:
        raise ToolError(f"{argv[0]} is not installed or not on PATH") from None
    except subprocess.TimeoutExpired:
        raise ToolError(f"{' '.join(argv)} still running after {timeout} s") from None
    return done.returncode
