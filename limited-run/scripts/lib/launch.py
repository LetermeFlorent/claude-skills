import os
import signal
import subprocess
import time
from pathlib import Path

import memory
import procs
import records
import tree
from common import FAILED, INTERRUPTED, SIGNAL_BASE, refuse, say

POLL_SECONDS = 0.5
STOP_SIGNALS = ("SIGTERM", "SIGINT", "SIGBREAK", "SIGHUP")


class Stopped(Exception):
    pass


def _raise_stopped(number, frame):
    raise Stopped(number)


def _catch_signals():
    for name in STOP_SIGNALS:
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), _raise_stopped)


def exit_code(returned):
    return SIGNAL_BASE - returned if returned < 0 else returned


def _wait(process):
    while True:
        try:
            return exit_code(process.wait(timeout=POLL_SECONDS))
        except subprocess.TimeoutExpired:
            continue


def _claim(folder, name, command, record):
    if name is None:
        name = records.claim_next(folder, command, record)
        if name is None:
            refuse("no free name left for this command, pass --name")
        return name
    if not records.valid_name(name):
        refuse(f"bad name {name!r}: letters, digits, dot, dash or underscore, 40 at most")
    if not records.claim(folder, name, record):
        refuse(f"a live task is already named {name}: pick another --name or stop it first")
    return name


def _run(folder, name, command, record):
    try:
        running = tree.spawn(command, record["cwd"], record["cap_mb"])
    except OSError as error:
        say(f"cannot start {command[0]}: {error}")
        return FAILED
    try:
        child = running.process.pid
        records.update(folder, name, {"child_pid": child, "child_created": procs.identity(child)})
        cap = f"cap {record['cap_mb']} MB" if record["cap_mb"] else "no memory cap"
        say(f"{name} pid {child}, {cap}, below normal priority")
        return _wait(running.process)
    except (Stopped, KeyboardInterrupt) as stop:
        tree.kill(running)
        return SIGNAL_BASE + stop.args[0] if isinstance(stop, Stopped) else INTERRUPTED
    finally:
        tree.close(running)


def start(command, name, cwd, ram_mb):
    if not command:
        refuse("no command after --")
    if ram_mb is not None and ram_mb < 0:
        refuse("--ram-mb must be 0 (no cap) or more")
    folder = records.state_dir()
    folder_of_task = Path(cwd or os.getcwd()).resolve()
    if not folder_of_task.is_dir():
        refuse(f"no such folder: {folder_of_task}")
    record = {"launcher_pid": os.getpid(), "launcher_created": procs.identity(os.getpid()), "command": command,
              "cwd": str(folder_of_task), "started": time.time(),
              "cap_mb": memory.cap_mb(memory.free_mb()) if ram_mb is None else ram_mb}
    name = _claim(folder, name, command, record)
    try:
        _catch_signals()
        return _run(folder, name, command, record)
    except (Stopped, KeyboardInterrupt):
        return INTERRUPTED
    finally:
        records.release(folder, name, os.getpid())
