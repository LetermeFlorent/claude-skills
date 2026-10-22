import random
import socket
import sys
import tempfile
from pathlib import Path

TOOL = "chrome-bidi"
LOCALHOST = "127.0.0.1"
DRIVER_OFFSET = 1000
ENCODING = "utf-8"
EXIT_INTERRUPTED = 130
POLL_STEP = 0.5
PORT_RANGE = (9300, 9900)
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
BIN_DIR = SCRIPTS_DIR.parent / "bin"
WORK_DIR = Path(tempfile.gettempdir()) / "claude-skills"


def guard(main, hint):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding=ENCODING, errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_INTERRUPTED)
    except Exception as error:
        print(f"{TOOL}: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(1)


def driver_port(port):
    return port + DRIVER_OFFSET


def local_url(port, path=""):
    return f"http://{LOCALHOST}:{port}{path}"


def profile_dir(port):
    return WORK_DIR / f"chrome-{port}"


def downloads_dir(profile):
    return profile.with_name(profile.name + "-downloads")


def split_value(value, count):
    parts = value.split("|", count - 1)
    return parts + [""] * (count - len(parts))


def port_free(port):
    with socket.socket() as probe:
        try:
            probe.bind((LOCALHOST, port))
        except OSError:
            return False
    return True


def free_port():
    first, last = PORT_RANGE
    span = last - first
    start = random.randrange(span)
    for offset in range(span):
        port = first + (start + offset) % span
        if not profile_dir(port).exists() and port_free(port) and port_free(driver_port(port)):
            return port
    raise RuntimeError(f"no free port pair between {first} and {last}")
