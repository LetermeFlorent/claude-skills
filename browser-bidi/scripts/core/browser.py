import contextlib
import shutil
import subprocess
import sys
import time
import urllib.error
from contextlib import contextmanager
from typing import NamedTuple

sys.dont_write_bytecode = True

from core.common import (BLANK, BROWSERS, DEFAULT_PROMPT, DEFAULT_SIZE, LOCAL, NAV_TIMEOUT, WORK_DIR, BidiError,
                    downloads_dir, driver_port, free_port, local_url, state_file)
from core.driver import CHROME, ensure_driver, find_firefox, write_prefs
from core.processes import kill, own_browser, own_driver, wait_gone
from core.session import create_session, first_context, open_session
from core.window import pick_desktop, show
from core.wsclient import WebSocketError


DETACHED = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
QUIET = DETACHED | subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS
MARIONETTE_FILE = "MarionetteActivePort"
READY_SECONDS = 20


def wait_http(url, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            with LOCAL.open(url, timeout=2):
                return True
        except urllib.error.HTTPError:
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
    if not wait_http(local_url(port, path), READY_SECONDS):
        raise TimeoutError(f"{name} on port {port} did not answer within {READY_SECONDS} s")


def marionette_port(profile):
    deadline = time.monotonic() + READY_SECONDS
    while time.monotonic() < deadline:
        with contextlib.suppress(OSError):
            if text := (profile / MARIONETTE_FILE).read_text().strip():
                return text
        time.sleep(0.5)
    raise TimeoutError(f"Firefox wrote no {MARIONETTE_FILE} within {READY_SECONDS} s")


def window_pid(port, fallback):
    entries = own_browser(port)
    pids = {entry["ProcessId"] for entry in entries}
    return next((entry["ProcessId"] for entry in entries if entry["ParentProcessId"] in pids), fallback)


class Launch(NamedTuple):
    url: str = BLANK
    size: tuple = DEFAULT_SIZE
    headless: bool = True
    login: bool = False
    prompt: str = DEFAULT_PROMPT
    browser: str = BROWSERS[0]


def browser_arguments(profile, size, headless, firefox):
    if firefox:
        return [str(find_firefox()), "-no-remote", "-profile", str(profile), "-width", str(size[0]),
                "-height", str(size[1])] + (["-headless"] if headless else [])
    return [str(CHROME), "--no-first-run", "--no-default-browser-check", "--disable-features=Translate",
            f"--user-data-dir={profile}", f"--window-size={size[0]},{size[1]}"] + (
        ["--headless=new", "--hide-scrollbars"] if headless else [])


def start(port, profile, launch=Launch()):
    url, size, headless, login, prompt, browser = launch
    firefox = browser == "firefox"
    driver, note = (None, "no driver in sign-in mode") if login else ensure_driver(browser)
    write_prefs(profile, browser)
    arguments = browser_arguments(profile, size, headless, firefox)
    if login:
        return spawn([*arguments, url], DETACHED).pid, note
    (profile / MARIONETTE_FILE).unlink(missing_ok=True)
    remote = [f"--remote-debugging-port={port}"] + (["-marionette"] if firefox else [])
    process = spawn([*arguments, *remote, BLANK], QUIET if headless else DETACHED)
    try:
        wait_ready(port, browser, "/json/version")
        state_file(port).unlink(missing_ok=True)
        attach = ["--connect-existing", "--marionette-port", marionette_port(profile)] if firefox else []
        spawn([str(driver), f"--port={driver_port(port)}", *attach], QUIET)
        wait_ready(driver_port(port), driver.stem, "/status")
        session = create_session(port, prompt, browser)
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
    return (window_pid(port, process.pid) if firefox else process.pid), note


def stop(port, session=None):
    closed = False
    try:
        with contextlib.suppress(OSError, WebSocketError, BidiError, KeyError):
            session = session or open_session(port)
            session.call("browser.close", {}, 10)
            closed = True
    finally:
        if session:
            session.close()
    forced = kill(wait_gone(port, 5 if closed else 0))
    drivers = kill(own_driver(port))
    state_file(port).unlink(missing_ok=True)
    return f"browser closed, port {port} released" + (f", forced pids {forced}" if forced else "") + (
        f", driver pids {drivers} stopped" if drivers else "")


def remove_tree(folder):
    for _ in range(10):
        shutil.rmtree(folder, ignore_errors=True)
        if not folder.exists():
            return
        time.sleep(0.5)


@contextmanager
def throwaway(size=DEFAULT_SIZE, visible=False, desktop_choice=None, browser=BROWSERS[0]):
    desktop = pick_desktop(desktop_choice) if visible else None
    port = free_port()
    profile = WORK_DIR / f"{browser}-{port}-run"
    session = None
    try:
        pid, _ = start(port, profile, Launch(size=size, headless=not visible, browser=browser))
        if visible:
            print(show(pid, desktop))
        session = open_session(port)
        yield session
    finally:
        print(stop(port, session))
        remove_tree(profile)
        remove_tree(downloads_dir(profile))
