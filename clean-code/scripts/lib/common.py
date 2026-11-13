import json
import re
import sys

ENCODING = "utf-8"
DECODE_ERRORS = "replace"
INDENT = 2
INTERRUPTED = 130
FAILED = 1
SECRET = re.compile(r"\b(sk_live_[0-9A-Za-z]{10,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|"
                    r"github_pat_[A-Za-z0-9_]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35})|"
                    r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
SECRET_FIELD = re.compile(r"(?P<field>password|passwd|secret|api[_-]?key|token|auth)[\"']?\s*[:=]\s*[\"']"
                          r"(?P<value>[^\"'\s$]{6,})[\"']", re.IGNORECASE)
SHOWN = 4


def mask(value):
    return f"{value[:SHOWN]}... ({len(value)} chars)"


def guard(main, hint):
    sys.stdout.reconfigure(encoding=ENCODING, errors=DECODE_ERRORS)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        print(f"clean-code: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(FAILED)


def read_json(path):
    return json.loads(path.read_text(encoding=ENCODING))


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=INDENT, ensure_ascii=False), encoding=ENCODING)


def compact(numbers):
    spans = []
    for number in sorted(set(numbers)):
        if spans and number == spans[-1][1] + 1:
            spans[-1][1] = number
        else:
            spans.append([number, number])
    return ", ".join(f"{first}" if first == last else f"{first}-{last}" for first, last in spans)
