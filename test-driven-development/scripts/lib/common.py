import sys
from dataclasses import dataclass, field

TOOL = "run.py"
ENCODING = "utf-8"
DECODE_ERRORS = "replace"
PASSED = 0
FAILED = 1
REFUSED = 2
INTERRUPTED = 130
SEPARATOR = "::"
RED, GREEN = "red", "green"


@dataclass
class Outcome:
    ran: int | None = None
    failed: int = 0
    errors: int = 0
    warnings: int = 0
    names: list = field(default_factory=list)
    reason: str | None = None


def counts_of(pattern, text):
    found = {}
    for number, word in pattern.findall(text):
        key = word.rstrip("s") if word.endswith(("errors", "warnings")) else word
        found[key] = found.get(key, 0) + int(number)
    return found


def guard(main, hint):
    sys.stdout.reconfigure(encoding=ENCODING, errors=DECODE_ERRORS)
    try:
        code = main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        print(f"{TOOL}: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(FAILED)
    sys.exit(code)
