import os
import sys

TOOL = "limited-run"
WINDOWS = os.name == "nt"
FAILED, REFUSED, INTERRUPTED = 1, 2, 130
SIGNAL_BASE = 128
MB = 1024 * 1024
ENCODING = "utf-8"


def say(text):
    print(f"{TOOL}: {text}", flush=True)


def refuse(problem):
    print(f"refused: {problem}", flush=True)
    sys.exit(REFUSED)


def guard(main, hint):
    sys.stdout.reconfigure(encoding=ENCODING, errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        say(f"{type(error).__name__}: {error}")
        print(f"by hand: {hint}", flush=True)
        sys.exit(FAILED)
