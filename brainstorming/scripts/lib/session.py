import os
import re
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from common import ENCODING, LOW_PRIORITY, WINDOWS, address, companion_root, read_json, run

INFO = "server.json"
LOG = "server.log"
CHOICES = "choices.json"
SCREENS = "screens"
STAMP = "%Y%m%d-%H%M%S"
SLUG = re.compile(r"[^a-z0-9]+")
DEFAULT_SLUG = "session"
DETACHED = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
START_WAIT = 10.0
STOP_WAIT = 5.0
STEP = 0.2
HTTP_TIMEOUT = 3
KEY_HEADER = "X-Key"
PYTHON = "python"
VERSION_ROUTE = "/version"
STOP_ROUTE = "/stop"
CHOICE_ROUTE = "/choice"
FILES_ROUTE = "/files/"


def slug(text):
    return SLUG.sub("-", text.lower()).strip("-") or DEFAULT_SLUG


def create(topic, root=None):
    folder = (root or companion_root()) / f"{slug(topic)}-{datetime.now().strftime(STAMP)}"
    (folder / SCREENS).mkdir(parents=True)
    return folder


def inside_root(folder, root=None):
    return folder.resolve().parent == (root or companion_root()).resolve()


def read_info(folder):
    info = read_json(folder / INFO) if (folder / INFO).exists() else None
    return info if isinstance(info, dict) else None


def spawn(script, folder, idle):
    command = [sys.executable, "-I", str(script), "serve", "--session", str(folder), "--idle", str(idle)]
    with open(folder / LOG, "a", encoding=ENCODING) as log:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=log, close_fds=True,
                                   creationflags=DETACHED | LOW_PRIORITY, start_new_session=not WINDOWS)
    return process.pid


def wait_for(check, limit):
    deadline = time.monotonic() + limit
    while time.monotonic() < deadline:
        found = check()
        if found:
            return found
        time.sleep(STEP)
    return check()


def process_name(pid):
    if not WINDOWS:
        try:
            os.kill(pid, 0)
        except OSError:
            return None
        return PYTHON
    code, out, _ = run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], Path.cwd())
    first = out.strip().split(",")[0].strip('"') if code == 0 and out.strip() else ""
    return first if first.lower().endswith(".exe") else None


def call(info, route, data=None):
    message = urllib.request.Request(address(info["port"], route), data=data, headers={KEY_HEADER: info["key"]})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(message, timeout=HTTP_TIMEOUT) as answer:
            return answer.status
    except OSError:
        return None


def halt(info):
    pid = info.get("pid")
    if call(info, STOP_ROUTE, b"") and wait_for(lambda: process_name(pid) is None, STOP_WAIT):
        return f"server stopped, pid {pid}"
    name = process_name(pid)
    if name is None:
        return f"server already gone, pid {pid}"
    if PYTHON not in name.lower():
        return f"pid {pid} is now {name}, not the server: left alone"
    os.kill(pid, signal.SIGTERM)
    wait_for(lambda: process_name(pid) is None, STOP_WAIT)
    return f"server killed, pid {pid}"
