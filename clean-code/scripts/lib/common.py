import json
import sys

ENCODING = "utf-8"
DECODE_ERRORS = "replace"
INDENT = 2
INTERRUPTED = 130
FAILED = 1


def guard(main, hint):
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
