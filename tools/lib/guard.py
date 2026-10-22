import sys

PREFIX = "claude-skills"
FAILED = 1


def run_guarded(main, hint):
    sys.stdout.reconfigure(errors="replace")
    try:
        return main()
    except Exception as error:
        print(f"{PREFIX}: {type(error).__name__}: {error}")
        print(hint)
        return FAILED
