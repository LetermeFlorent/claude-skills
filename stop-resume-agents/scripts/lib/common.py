import os
import sys

MARKER = "<!-- stop-resume-agents v1 -->"
FAILED = 2
INTERRUPTED = 130


def config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def guard(main, hint):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        print(f"{error!r}. {hint}")
        sys.exit(FAILED)
