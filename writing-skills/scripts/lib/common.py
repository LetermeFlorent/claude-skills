import sys
from pathlib import Path

TOOL = "check_skill"
ENCODING = "utf-8"
DECODE_ERRORS = "replace"
FAILED, REFUSED, INTERRUPTED = 1, 2, 130
LEVELS = REFUSE, CHECK, NOTE = ("refused", "check", "note")
NO_LINE = 0


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


def read_text(path):
    try:
        return Path(path).read_text(encoding=ENCODING)
    except (OSError, UnicodeDecodeError):
        return None


def relative(path, folder):
    return Path(path).relative_to(folder).as_posix()


def _place(item):
    _, where, line, _ = item
    return f"{where}:{line}" if line else where


def show(findings):
    ordered = sorted(findings, key=lambda item: (LEVELS.index(item[0]), item[1], item[2]))
    for item in ordered:
        print(f"{item[0]}: {_place(item)} {item[3]}")
    counts = [sum(1 for item in findings if item[0] == level) for level in LEVELS]
    print("{} refused, {} to check, {} notes".format(*counts))
    return counts[0]
