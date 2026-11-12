import base64
import json
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True

from core.common import driver_port


def powershell(script, timeout=60):
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    done = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if done.returncode != 0:
        raise RuntimeError(f"powershell failed: {done.stderr.strip()[:300]}")
    return done.stdout.strip()


def as_list(text):
    found = json.loads(text) if text else []
    return found if isinstance(found, list) else [found]


def process_table(names=()):
    query = " -Filter \"" + " or ".join(f"Name='{name}'" for name in names) + "\"" if names else ""
    return as_list(powershell("[Console]::OutputEncoding = [Text.Encoding]::UTF8; Get-CimInstance Win32_Process"
                              f"{query} | Select-Object ProcessId,ParentProcessId,Name,CommandLine | "
                              "ConvertTo-Json -Compress"))


def matching(names, flag):
    pattern = re.compile(re.escape(flag) + r"(?![0-9])")
    return [entry for entry in process_table(names) if pattern.search(entry.get("CommandLine") or "")
            and not any(child in entry["CommandLine"] for child in ("--type=", "-contentproc"))]


def own_browser(port):
    return matching(("chrome.exe", "firefox.exe"), f"--remote-debugging-port={port}")


def own_driver(port):
    return matching(("chromedriver.exe", "geckodriver.exe"), f"--port={driver_port(port)}")


def kill(entries):
    for entry in entries:
        subprocess.run(["taskkill", "/PID", str(entry["ProcessId"]), "/T", "/F"], capture_output=True)
    return [entry["ProcessId"] for entry in entries]


def wait_gone(port, seconds):
    deadline = time.monotonic() + seconds
    while (left := own_browser(port)) and time.monotonic() < deadline:
        time.sleep(0.5)
    return left
