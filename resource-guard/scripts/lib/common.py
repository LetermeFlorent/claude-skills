import sys

TOOL = "resource-guard"
ENCODING = "utf-8"
DECODE_ERRORS = "replace"
OK, NOT_OK, BLOCKED, FAILED, INTERRUPTED = 0, 1, 2, 1, 130


def say_error(text):
    print(text, file=sys.stderr, flush=True)


def _readable_streams():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding=ENCODING, errors=DECODE_ERRORS)


def guard(main, hint):
    _readable_streams()
    try:
        code = main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        say_error(f"{TOOL}: {type(error).__name__}: {error}")
        say_error(f"by hand: {hint}")
        sys.exit(FAILED)
    sys.exit(code)
