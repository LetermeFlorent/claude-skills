import contextlib
import shutil
import subprocess
import time
import urllib.error
from contextlib import contextmanager
from dataclasses import dataclass

from core.binaries import chrome_exe, ensure_driver
from core.common import POLL_STEP, WORK_DIR, downloads_dir, driver_port, free_port, local_url
from core.preferences import write_prefs
from core.processes import kill, own_driver, wait_gone
from core.session import DEFAULT_PROMPT, LOCAL, BidiError, create_session, open_session, state_file
from core.wsclient import WebSocketError
from window.desktops import pick_desktop, show

DEFAULT_SIZE = (1280, 720)
BLANK = "about:blank"
NAV_TIMEOUT = 120
START_TIMEOUT = 20
CLOSE_TIMEOUT = 10
CLOSE_GRACE = 5
CLEAN_TRIES = 10
HTTP_PROBE_TIMEOUT = 2
CHROME_FLAGS = ("--no-first-run", "--no-default-browser-check", "--disable-features=Translate")
HEADLESS_FLAGS = ("--headless=new", "--hide-scrollbars")
DETACHED = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
QUIET = DETACHED | subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS


def wait_http(url, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            with LOCAL.open(url, timeout=HTTP_PROBE_TIMEOUT):
                return True
        except (OSError, urllib.error.URLError):
            time.sleep(POLL_STEP)
    return False


def spawn(arguments, flags):
    try:
        return subprocess.Popen(arguments, creationflags=flags | subprocess.CREATE_BREAKAWAY_FROM_JOB,
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        return subprocess.Popen(arguments, creationflags=flags, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_ready(port, name, url):
    if not wait_http(url, START_TIMEOUT):
        raise TimeoutError(f"{name} on port {port} did not answer within {START_TIMEOUT} s")


def first_context(session):
    return session.call("browsingContext.getTree")["contexts"][0]["context"]


@dataclass(frozen=True)
class LaunchOptions:
    url: str = BLANK
    size: tuple = DEFAULT_SIZE
    headless: bool = True
    login: bool = False
    prompt: str = DEFAULT_PROMPT


def open_first_page(port, url, viewport_size, prompt):
    session = create_session(port, prompt)
    try:
        context = first_context(session)
        if viewport_size:
            viewport = {"width": viewport_size[0], "height": viewport_size[1]}
            session.call("browsingContext.setViewport", {"context": context, "viewport": viewport})
        if url != BLANK:
            session.call("browsingContext.navigate", {"context": context, "url": url, "wait": "complete"}, NAV_TIMEOUT)
    finally:
        session.close()


def start(port, profile, settings):
    driver, driver_note = (None, "no driver in sign-in mode") if settings.login else ensure_driver()
    write_prefs(profile)
    width, height = settings.size
    arguments = [str(chrome_exe()), *CHROME_FLAGS, f"--user-data-dir={profile}", f"--window-size={width},{height}"]
    arguments += [*HEADLESS_FLAGS] if settings.headless else []
    if settings.login:
        return spawn([*arguments, settings.url], DETACHED).pid, driver_note
    chrome = spawn([*arguments, f"--remote-debugging-port={port}", BLANK], QUIET if settings.headless else DETACHED)
    try:
        wait_ready(port, "Chrome", local_url(port, "/json/version"))
        state_file(port).unlink(missing_ok=True)
        spawn([str(driver), f"--port={driver_port(port)}"], QUIET)
        wait_ready(driver_port(port), "chromedriver", local_url(driver_port(port), "/status"))
        open_first_page(port, settings.url, settings.size if settings.headless else None, settings.prompt)
    except (OSError, BidiError, WebSocketError, KeyError):
        stop(port)
        raise
    return chrome.pid, driver_note


def stop(port, session=None):
    try:
        with contextlib.suppress(OSError, WebSocketError, BidiError, KeyError):
            session = session or open_session(port)
            session.call("browser.close", {}, CLOSE_TIMEOUT)
    finally:
        if session:
            session.close()
    forced = kill(wait_gone(port, CLOSE_GRACE))
    drivers = kill(own_driver(port))
    state_file(port).unlink(missing_ok=True)
    return f"browser closed, port {port} released" + (f", forced pids {forced}" if forced else "") + (
        f", chromedriver pids {drivers} stopped" if drivers else "")


def remove_tree(folder):
    for _ in range(CLEAN_TRIES):
        shutil.rmtree(folder, ignore_errors=True)
        if not folder.exists():
            return
        time.sleep(POLL_STEP)


@contextmanager
def throwaway(size=DEFAULT_SIZE, visible=False, desktop_choice=None):
    desktop = pick_desktop(desktop_choice) if visible else None
    port = free_port()
    profile = WORK_DIR / f"chrome-{port}-run"
    session = None
    try:
        pid, _ = start(port, profile, LaunchOptions(size=size, headless=not visible))
        if visible:
            print(show(pid, desktop))
        session = open_session(port)
        yield session
    finally:
        print(stop(port, session))
        remove_tree(profile)
        remove_tree(downloads_dir(profile))
