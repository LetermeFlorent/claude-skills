import argparse
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

import launch
import records
import tree
from common import REFUSED, guard, refuse, say

HINT = 'python -I "<skill>/scripts/run.py" list, then stop the task by hand (taskkill /T /F /PID <pid>, or kill)'
COMMAND_WIDTH = 60
ELLIPSIS = "..."
MINUTE, HOUR = 60, 3600


def arguments():
    parser = argparse.ArgumentParser(description="Run task processes with a RAM cap and low priority, list them, "
                                                 "stop them.")
    actions = parser.add_subparsers(dest="action", required=True)
    start = actions.add_parser("start", help="run a command under a cap and wait for it")
    start.add_argument("--ram-mb", type=int, help="cap in MB for the whole tree; default half the free RAM, "
                                                  "512 to 4096; 0 means no memory cap")
    start.add_argument("--name", help="task name; default the command's first word plus a counter")
    start.add_argument("--cwd", help="folder to run the command in")
    start.add_argument("--queue", type=int, default=0, help="with --name: seconds to wait for a live task of that "
                                                            "name to end, instead of refusing")
    start.add_argument("command", nargs=argparse.REMAINDER, help="-- then the command and its arguments")
    actions.add_parser("list", help="one line per live task started by this tool")
    stop = actions.add_parser("stop", help="stop a task started by this tool, with its whole tree")
    stop.add_argument("target", nargs="?", help="task name or pid")
    stop.add_argument("--all", action="store_true", help="stop every live task started by this tool")
    return parser.parse_args()


def age(seconds):
    seconds = max(0, int(seconds))
    if seconds < MINUTE:
        return f"{seconds}s"
    if seconds < HOUR:
        return f"{seconds // MINUTE}m{seconds % MINUTE:02d}s"
    return f"{seconds // HOUR}h{seconds % HOUR // MINUTE:02d}m"


def shorten(command):
    text = " ".join(str(part) for part in command)
    return text if len(text) <= COMMAND_WIDTH else text[:COMMAND_WIDTH - len(ELLIPSIS)] + ELLIPSIS


def describe(record, now):
    pid = record.get("child_pid") or record.get("launcher_pid")
    cap = f"cap {record.get('cap_mb')} MB" if record.get("cap_mb") else "no cap"
    return f"{record.get('name')}  pid {pid}  age {age(now - record.get('started', now))}  {cap}  " \
           f"{shorten(record.get('command', []))}"


def matches(record, target):
    return target in (record.get("name"), str(record.get("launcher_pid")), str(record.get("child_pid")))


def show_list():
    found = records.live_records(records.state_dir())
    now = time.time()
    for record in found:
        print(describe(record, now))
    say(f"{len(found)} live task(s)")
    return 0


def stop(target, every):
    if bool(target) == every:
        refuse("stop takes a task name or pid, or --all")
    folder = records.state_dir()
    chosen = [record for record in records.live_records(folder) if every or matches(record, target)]
    if not chosen:
        say("nothing to stop" if every else f"no live task {target} started by this tool")
        return 0 if every else REFUSED
    for record in chosen:
        tree.kill_recorded(record)
        records.forget(folder, record["name"])
        say(f"stopped {record['name']} pid {record.get('child_pid') or record.get('launcher_pid')}")
    return 0


def main():
    options = arguments()
    if options.action == "list":
        sys.exit(show_list())
    if options.action == "stop":
        sys.exit(stop(options.target, options.all))
    command = options.command[1:] if options.command[:1] == ["--"] else options.command
    sys.exit(launch.start(command, options))


if __name__ == "__main__":
    guard(main, HINT)
