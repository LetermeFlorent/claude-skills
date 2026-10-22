import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.browser import DEFAULT_SIZE, LaunchOptions, start
from core.session import DEFAULT_PROMPT
from core.common import downloads_dir, driver_port, free_port, guard, profile_dir
from core.processes import own_chrome
from window.desktops import pick_desktop, show

PROMPT_CHOICES = (DEFAULT_PROMPT, "accept", "ignore")


def size_of(text):
    width, _, height = text.lower().partition("x")
    return int(width), int(height)


def main():
    parser = argparse.ArgumentParser(
        description="Start Chrome with a debugging port, its own profile and chromedriver.")
    parser.add_argument("--port", type=int, help="debugging port, a free one is picked when missing")
    parser.add_argument("--url", default="about:blank")
    parser.add_argument("--size", type=size_of, default=DEFAULT_SIZE, help="content area, WIDTHxHEIGHT")
    parser.add_argument("--visible", action="store_true", help="show a window, only when the user asked to watch")
    parser.add_argument("--login", action="store_true", help="no remote control, for a human sign-in")
    parser.add_argument("--desktop", help="virtual desktop index, or 'current'")
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--prompt", choices=PROMPT_CHOICES, default=DEFAULT_PROMPT,
                        help="what the session does with an alert; ignore leaves it to the prompt action")
    options = parser.parse_args()
    if options.login and not options.visible:
        raise ValueError("--login opens a window for a human sign-in, so it needs --visible as well")
    port = options.port or free_port()
    running = own_chrome(port)
    if running:
        print(f"already running, pid {running[0]['ProcessId']}, port {port}")
        return
    desktop = pick_desktop(options.desktop) if options.visible and not options.login else None
    profile = options.profile or profile_dir(port)
    settings = LaunchOptions(options.url, options.size, not options.visible, options.login, options.prompt)
    pid, driver_note = start(port, profile, settings)
    if options.login:
        print(f"chrome started WITHOUT remote control for sign-in, pid {pid}, profile {profile}")
        print(f"once signed in, close the window and start again with --port {port} and without --login")
        return
    print(f"chrome started, pid {pid}, port {port}, driver {driver_port(port)}, profile {profile}, "
          f"downloads {downloads_dir(profile)}")
    print(driver_note)
    if options.visible:
        print(show(pid, desktop))


if __name__ == "__main__":
    guard(main, "start chrome.exe with --remote-debugging-port=<port> "
                "--user-data-dir=<Temp>/claude-skills/chrome-<port>, "
                "then bin/chromedriver.exe --port=<port+1000>")
