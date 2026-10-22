import base64
import json
import re
import subprocess
import time

from core.common import POLL_STEP, driver_port

POWERSHELL = ("powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand")
POWERSHELL_TIMEOUT = 60
CHILD_FLAG = "--type="


def powershell(script, timeout=POWERSHELL_TIMEOUT):
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    done = subprocess.run([*POWERSHELL, encoded], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)
    if done.returncode != 0:
        raise RuntimeError(f"powershell failed: {done.stderr.strip()[:300]}")
    return done.stdout.strip()


def as_list(text):
    found = json.loads(text) if text else []
    return found if isinstance(found, list) else [found]


def table(name=None):
    query = f" -Filter \"Name='{name}'\"" if name else ""
    script = (f"[Console]::OutputEncoding = [Text.Encoding]::UTF8; Get-CimInstance Win32_Process{query} | "
              "Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress")
    return as_list(powershell(script))


def matching(name, flag):
    pattern = re.compile(re.escape(flag) + r"(?![0-9])")
    return [entry for entry in table(name)
            if pattern.search(entry.get("CommandLine") or "") and CHILD_FLAG not in entry["CommandLine"]]


def own_chrome(port):
    return matching("chrome.exe", f"--remote-debugging-port={port}")


def own_driver(port):
    return matching("chromedriver.exe", f"--port={driver_port(port)}")


def kill(entries):
    for entry in entries:
        subprocess.run(["taskkill", "/PID", str(entry["ProcessId"]), "/T", "/F"], capture_output=True)
    return [entry["ProcessId"] for entry in entries]


def wait_gone(port, seconds):
    deadline = time.monotonic() + seconds
    while (left := own_chrome(port)) and time.monotonic() < deadline:
        time.sleep(POLL_STEP)
    return left
