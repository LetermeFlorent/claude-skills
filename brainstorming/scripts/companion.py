import sys

sys.dont_write_bytecode = True
import argparse
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from choices import load, summary
from common import HOST, companion_root, guard, refuse
from page import newest
from server import serve
from session import (CHOICES, LOG, SCREENS, START_WAIT, VERSION_ROUTE, call, create, halt, inside_root, read_info,
                     spawn, wait_for)

IDLE_MINUTES = 120
SCRIPT = Path(__file__).resolve()
HINT = (f"python -I -m http.server --bind {HOST} --directory <screens folder>; "
        f"sessions live in {companion_root().as_posix()}")


def parser():
    root = argparse.ArgumentParser(prog="companion.py")
    commands = root.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("--topic", required=True)
    start.add_argument("--idle", type=int, default=IDLE_MINUTES)
    worker = commands.add_parser("serve")
    worker.add_argument("--session", required=True)
    worker.add_argument("--idle", type=int, default=IDLE_MINUTES)
    for name in ("status", "choices"):
        commands.add_parser(name).add_argument("--session", required=True)
    halt_command = commands.add_parser("stop")
    halt_command.add_argument("--session", required=True)
    halt_command.add_argument("--keep", action="store_true")
    return root


def session_folder(text):
    folder = Path(text).resolve()
    if not inside_root(folder) or not folder.is_dir():
        refuse([f"{folder.as_posix()} is not a companion session in {companion_root().as_posix()}"])
    return folder


def start(arguments):
    if arguments.idle < 1:
        refuse(["--idle takes a number of minutes, 1 or more"])
    folder = create(arguments.topic)
    pid = spawn(SCRIPT, folder, arguments.idle)
    info = wait_for(lambda: read_info(folder), START_WAIT)
    if info is None:
        raise RuntimeError(f"the server, pid {pid}, did not start: read {(folder / LOG).as_posix()}")
    print(f"session: {folder.as_posix()}")
    print(f"screens: {(folder / SCREENS).as_posix()}")
    print(f"url: {info['url']}")
    print(f"log: {(folder / LOG).as_posix()}")
    print(f'stop: python -I "{SCRIPT.as_posix()}" stop --session "{folder.as_posix()}"')


def status(arguments):
    folder = session_folder(arguments.session)
    info = read_info(folder)
    alive = info is not None and call(info, VERSION_ROUTE) is not None
    print(f"server: running, pid {info['pid']}, {info['url']}" if alive else "server: stopped")
    screen = newest(folder / SCREENS)
    print(f"newest screen: {screen.name if screen else 'none'}")


def choices(arguments):
    for line in summary(load(session_folder(arguments.session) / CHOICES)):
        print(line)


def stop(arguments):
    folder = session_folder(arguments.session)
    for line in summary(load(folder / CHOICES)):
        print(line)
    info = read_info(folder)
    print(halt(info) if info else "server: not running")
    if arguments.keep:
        print(f"kept: {folder.as_posix()}")
        return
    shutil.rmtree(folder)
    print(f"removed: {folder.as_posix()}")


def worker(arguments):
    serve(session_folder(arguments.session), arguments.idle)


def main():
    arguments = parser().parse_args()
    actions = {"start": start, "serve": worker, "status": status, "choices": choices, "stop": stop}
    actions[arguments.command](arguments)


if __name__ == "__main__":
    guard(main, HINT)
