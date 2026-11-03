import argparse
import json
import sys
import time

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

import limits
import metrics
from common import BLOCKED, DECODE_ERRORS, ENCODING, NOT_OK, OK, TOOL, guard, say_error
from heavy import is_heavy
from payload import command_of

HINT = 'python -I "<skill>/scripts/guard.py" check'
POLL_SECONDS = 5.0
FLAGS = (("ram_gb", "--ram-gb", "free RAM in GB"), ("cpu", "--cpu", "CPU load in %"),
         ("disk", "--disk", "disk busy time in %"), ("timeout", "--timeout", "seconds to wait"))


def arguments():
    parser = argparse.ArgumentParser(prog="guard.py", description="Wait for room before a heavy command.")
    shared = argparse.ArgumentParser(add_help=False)
    for key, flag, meaning in FLAGS:
        shared.add_argument(flag, dest=key, type=float, default=None, help=f"{meaning} (env {limits.ENV_NAMES[key]})")
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("check", parents=[shared], help="one status line; exit 0 when ok, 1 when not")
    actions.add_parser("wait", parents=[shared], help="re-check until ok; exit 0 when ok, 2 on timeout")
    actions.add_parser("hook", help="pre-tool hook: JSON event on stdin; exit 2 blocks the call")
    return parser.parse_args()


def measure(chosen):
    current = metrics.sample()
    return current, limits.reasons(current, chosen)


def wait_for_room(chosen, say):
    current, found = measure(chosen)
    if limits.low_disk(current, chosen):
        say(limits.disk_warning(current, chosen))
    if not found:
        return current, found, 0.0
    start = time.monotonic()
    say(f"{TOOL}: waiting up to {chosen['timeout']:g} s ({', '.join(found)})")
    while found and time.monotonic() - start < chosen["timeout"]:
        time.sleep(max(0.0, min(POLL_SECONDS, chosen["timeout"] - (time.monotonic() - start))))
        current, found = measure(chosen)
    return current, found, time.monotonic() - start


def check(chosen):
    current, found = measure(chosen)
    print(limits.status_line(current, found))
    if limits.low_disk(current, chosen):
        print(limits.disk_warning(current, chosen))
    return NOT_OK if found else OK


def wait(chosen):
    current, found, waited = wait_for_room(chosen, print)
    if found:
        print(f"{TOOL}: timeout after {waited:.0f} s, still {', '.join(found)}")
        return BLOCKED
    print(limits.status_line(current, found) + (f" after {waited:.0f} s" if waited else ""))
    return OK


def hook():
    try:
        event = json.loads(sys.stdin.buffer.read().decode(ENCODING, DECODE_ERRORS))
    except (OSError, ValueError, AttributeError):
        return OK
    if not is_heavy(command_of(event)):
        return OK
    current, found, waited = wait_for_room(limits.resolve(), say_error)
    if not found:
        return OK
    say_error(f"{TOOL}: the command was not run: after {waited:.0f} s of waiting the PC is still short "
              f"({', '.join(found)}). Other sessions are busy: retry later, or run one heavy job at a time.")
    return BLOCKED


def main():
    options = arguments()
    if options.action == "hook":
        return hook()
    chosen = limits.resolve({key: getattr(options, key) for key, _, _ in FLAGS})
    return check(chosen) if options.action == "check" else wait(chosen)


if __name__ == "__main__":
    guard(main, HINT)
