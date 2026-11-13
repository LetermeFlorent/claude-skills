import os
import shutil
import signal
import subprocess
import time

import procs
from common import MB, WINDOWS

CREATE_SUSPENDED = 0x4
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
NICE = 10
GRACE_SECONDS, STEP_SECONDS = 3.0, 0.1
TASKKILL_TIMEOUT = 30


class Tree:
    def __init__(self, process, job):
        self.process, self.job = process, job


def resolve(command):
    return [shutil.which(command[0]) or command[0], *command[1:]]


def _spawn_windows(argv, cwd, cap_mb):
    import winapi
    job = winapi.create_job(cap_mb)
    try:
        process = subprocess.Popen(argv, cwd=cwd, creationflags=CREATE_SUSPENDED | subprocess.CREATE_NEW_PROCESS_GROUP)
    except BaseException:
        winapi.close_job(job)
        raise
    try:
        winapi.adopt_and_resume(job, process.pid)
    except BaseException:
        process.kill()
        process.wait()
        winapi.close_job(job)
        raise
    return Tree(process, job)


def _limits(cap_mb):
    def apply():
        import resource
        os.nice(NICE)
        if cap_mb:
            _, hard = resource.getrlimit(resource.RLIMIT_AS)
            size = cap_mb * MB if hard == resource.RLIM_INFINITY else min(cap_mb * MB, hard)
            resource.setrlimit(resource.RLIMIT_AS, (size, hard))
    return apply


def spawn(command, cwd, cap_mb):
    argv = resolve(command)
    if WINDOWS:
        return _spawn_windows(argv, cwd, cap_mb)
    return Tree(subprocess.Popen(argv, cwd=cwd, start_new_session=True, preexec_fn=_limits(cap_mb)), None)


def _group_alive(group):
    try:
        os.killpg(group, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def kill_group(group):
    for number in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(group, number)
        except ProcessLookupError:
            return
        deadline = time.monotonic() + GRACE_SECONDS
        while _group_alive(group) and time.monotonic() < deadline:
            time.sleep(STEP_SECONDS)


def kill(tree):
    if WINDOWS:
        import winapi
        winapi.terminate_job(tree.job)
    else:
        kill_group(tree.process.pid)


def close(tree):
    if WINDOWS:
        import winapi
        winapi.close_job(tree.job)


def _taskkill(pid):
    subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True,
                   timeout=TASKKILL_TIMEOUT, creationflags=NO_WINDOW)


def kill_recorded(record):
    launcher, child = record.get("launcher_pid"), record.get("child_pid")
    if not WINDOWS:
        if child and procs.same(child, record.get("child_created")):
            kill_group(child)
        return
    if procs.same(launcher, record.get("launcher_created")):
        _taskkill(launcher)
    if child and procs.same(child, record.get("child_created")):
        _taskkill(child)
