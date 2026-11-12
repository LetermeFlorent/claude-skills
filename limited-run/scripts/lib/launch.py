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
QUEUE_PAUSE = 2
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


def _claim(folder, name, record, queue):
    if name is None:
        name = records.claim_next(folder, record["command"], record)
        if name is None:
            refuse("no free name left for this command, pass --name")
        return name, False
    if not records.valid_name(name):
        refuse(f"bad name {name!r}: letters, digits, dot, dash or underscore, 40 at most")
    deadline = time.monotonic() + queue
    waited = False
    while not records.claim(folder, name, record):
        if time.monotonic() >= deadline:
            refuse(f"a live task is already named {name}: pick another --name or stop it first")
        if not waited:
            say(f"waiting for {name}")
            waited = True
        time.sleep(QUEUE_PAUSE)
    return name, waited


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


def _fresh(ram_mb):
    return {"started": time.time(), "cap_mb": memory.cap_mb(memory.free_mb()) if ram_mb is None else ram_mb}


def start(command, options):
    if not command:
        refuse("no command after --")
    if options.ram_mb is not None and options.ram_mb < 0:
        refuse("--ram-mb must be 0 (no cap) or more")
    if options.queue < 0:
        refuse("--queue must be 0 or more")
    folder = records.state_dir()
    folder_of_task = Path(options.cwd or os.getcwd()).resolve()
    if not folder_of_task.is_dir():
        refuse(f"no such folder: {folder_of_task}")
    record = {"launcher_pid": os.getpid(), "launcher_created": procs.identity(os.getpid()), "command": command,
              "cwd": str(folder_of_task), **_fresh(options.ram_mb)}
    name, waited = _claim(folder, options.name, record, options.queue)
    if waited:
        fresh = _fresh(options.ram_mb)
        record.update(fresh)
        records.update(folder, name, fresh)
    try:
        _catch_signals()
        return _run(folder, name, command, record)
    except (Stopped, KeyboardInterrupt):
        return INTERRUPTED
    finally:
        records.release(folder, name, os.getpid())
