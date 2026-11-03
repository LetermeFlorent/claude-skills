import contextlib
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from typing import NamedTuple

sys.dont_write_bytecode = True

from core.common import (BLANK, DEFAULT_PROMPT, DEFAULT_SIZE, LOCAL, NAV_TIMEOUT, WORK_DIR, BidiError, downloads_dir,
                    driver_port, free_port, local_url, state_file)
from core.driver import CHROME, ensure_driver, write_prefs
from core.processes import kill, own_driver, wait_gone
from core.session import create_session, first_context, open_session
from core.window import pick_desktop, show
from core.wsclient import WebSocketError


DETACHED = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
QUIET = DETACHED | subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS


def wait_http(url, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            with LOCAL.open(url, timeout=2):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def spawn(arguments, flags):
    streams = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    try:
        return subprocess.Popen(arguments, creationflags=flags | subprocess.CREATE_BREAKAWAY_FROM_JOB, **streams)
    except OSError:
        return subprocess.Popen(arguments, creationflags=flags, **streams)


def wait_ready(port, name, path):
    if not wait_http(local_url(port, path), 20):
        raise TimeoutError(f"{name} on port {port} did not answer within 20 s")


class Launch(NamedTuple):
    url: str = BLANK
    size: tuple = DEFAULT_SIZE
    headless: bool = True
    login: bool = False
    prompt: str = DEFAULT_PROMPT


def start(port, profile, launch=Launch()):
    url, size, headless, login, prompt = launch
    driver, note = (None, "no driver in sign-in mode") if login else ensure_driver()
    write_prefs(profile)
    arguments = [str(CHROME), "--no-first-run", "--no-default-browser-check", "--disable-features=Translate",
                 f"--user-data-dir={profile}", f"--window-size={size[0]},{size[1]}"]
    if headless:
        arguments += ["--headless=new", "--hide-scrollbars"]
    if login:
        return spawn([*arguments, url], DETACHED).pid, note
    chrome = spawn([*arguments, f"--remote-debugging-port={port}", BLANK], QUIET if headless else DETACHED)
    try:
        wait_ready(port, "Chrome", "/json/version")
        state_file(port).unlink(missing_ok=True)
        spawn([str(driver), f"--port={driver_port(port)}"], QUIET)
        wait_ready(driver_port(port), "chromedriver", "/status")
        session = create_session(port, prompt)
        try:
            context = first_context(session)
            if headless:
                session.call("browsingContext.setViewport",
                             {"context": context, "viewport": {"width": size[0], "height": size[1]}})
            if url != BLANK:
                session.call("browsingContext.navigate", {"context": context, "url": url, "wait": "complete"},
                             NAV_TIMEOUT)
        finally:
            session.close()
    except (OSError, BidiError, WebSocketError, KeyError):
        stop(port)
        raise
    return chrome.pid, note


def stop(port, session=None):
    try:
        with contextlib.suppress(OSError, WebSocketError, BidiError, KeyError):
            session = session or open_session(port)
            session.call("browser.close", {}, 10)
    finally:
        if session:
            session.close()
    forced = kill(wait_gone(port, 5))
    drivers = kill(own_driver(port))
    state_file(port).unlink(missing_ok=True)
    return f"browser closed, port {port} released" + (f", forced pids {forced}" if forced else "") + (
        f", chromedriver pids {drivers} stopped" if drivers else "")


def remove_tree(folder):
    for _ in range(10):
        shutil.rmtree(folder, ignore_errors=True)
        if not folder.exists():
            return
        time.sleep(0.5)


@contextmanager
def throwaway(size=DEFAULT_SIZE, visible=False, desktop_choice=None):
    desktop = pick_desktop(desktop_choice) if visible else None
    port = free_port()
    profile = WORK_DIR / f"chrome-{port}-run"
    session = None
    try:
        pid, _ = start(port, profile, Launch(size=size, headless=not visible))
        if visible:
            print(show(pid, desktop))
        session = open_session(port)
        yield session
    finally:
        print(stop(port, session))
        remove_tree(profile)
        remove_tree(downloads_dir(profile))
