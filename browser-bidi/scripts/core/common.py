import json
import random
import socket
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


LOCALHOST = "127.0.0.1"
WORK_DIR = Path(tempfile.gettempdir()) / "claude-skills"
BIN_DIR = Path(__file__).resolve().parents[2] / "bin"
COMMAND_TIMEOUT = 30
NAV_TIMEOUT = 120
BLANK = "about:blank"
DEFAULT_SIZE = (1280, 720)
DEFAULT_PROMPT = "dismiss"
BROWSERS = ("chrome", "firefox")
LOCAL = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class BidiError(Exception):
    pass


def guard(main, hint):
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as error:
        print(f"browser-bidi: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(1)


def driver_port(port):
    return port + 1000


def local_url(port, path=""):
    return f"http://{LOCALHOST}:{port}{path}"


def profile_dir(port, browser=BROWSERS[0]):
    return WORK_DIR / f"{browser}-{port}"


def downloads_dir(profile):
    return profile.with_name(profile.name + "-downloads")


def state_file(port):
    return WORK_DIR / f"bidi-{port}.session"


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
    start = random.randrange(600)
    for offset in range(600):
        port = 9300 + (start + offset) % 600
        used = any(profile_dir(port, browser).exists() for browser in BROWSERS)
        if not used and port_free(port) and port_free(driver_port(port)):
            return port
    raise RuntimeError("no free port pair between 9300 and 9900")


def http_json(method, url, body=None, timeout=COMMAND_TIMEOUT):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with LOCAL.open(request, timeout=timeout) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        try:
            detail = json.loads(error.read() or b"{}").get("value") or {}
        except ValueError:
            detail = {}
        raise BidiError(f"{detail.get('error', error.code)}: {detail.get('message', error.reason)}") from None
