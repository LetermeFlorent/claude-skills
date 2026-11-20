import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from blender import INSIDE, KEEP_PREFS, LOW_PRIORITY, BLEND

QUEUE = Path(tempfile.gettempdir()) / "blender-live"
POLL = 0.3
START = 120
EXIT_MARK = "@@exit "
WINDOWS = os.name == "nt"


def alive(pid):
    if WINDOWS:
        listed = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True)
        return str(pid) in listed.stdout
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def running_pid(queue):
    ready = queue / "ready"
    if not ready.exists():
        return None
    pid = int(ready.read_text(encoding="utf-8") or 0)
    return pid if pid and alive(pid) else None


def own_prefs(exe, queue):
    env = dict(os.environ, BLENDER_USER_RESOURCES=str(queue / "home"))
    save = "import bpy; bpy.context.preferences.view.show_splash = False; bpy.ops.wm.save_userpref()"
    subprocess.run([exe, "--background", "--python-expr", save], capture_output=True, env=env,
                   timeout=START, creationflags=LOW_PRIORITY)
    return env


def open_window(exe, source, queue):
    shutil.rmtree(queue, ignore_errors=True)
    queue.mkdir(parents=True)
    env = None if os.environ.get(KEEP_PREFS) == "1" else own_prefs(exe, queue)
    opened = [source] if source and source.lower().endswith(BLEND) else []
    argv = [exe, *opened, "--python", str(INSIDE / "live_bl.py"), "--", str(queue)]
    detached = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    with open(queue / "blender.log", "w", encoding="utf-8") as log:
        subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env,
                         creationflags=detached | LOW_PRIORITY, start_new_session=not WINDOWS)


def wait_for(path, timeout, pid=None):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if path.exists():
            return True
        if pid and not alive(pid):
            return False
        time.sleep(POLL)
    return False


def send(queue, pid, script_text, timeout):
    name = f"{time.time_ns()}.py"
    part = queue / "in" / (name + ".part")
    part.write_text(script_text, encoding="utf-8")
    part.replace(queue / "in" / name)
    result = queue / "out" / (name + ".txt")
    if not wait_for(result, timeout, pid):
        return None, "no answer: the Blender window was closed or the step is still running"
    text = result.read_text(encoding="utf-8")
    result.unlink()
    body, _, code = text.rpartition(EXIT_MARK)
    return int(code.strip() or 1), body.rstrip()


def close(queue, pid, timeout):
    (queue / "stop").write_text("stop", encoding="utf-8")
    end = time.monotonic() + timeout
    while time.monotonic() < end and alive(pid):
        time.sleep(POLL)
    if alive(pid):
        if WINDOWS:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
    closed = not alive(pid)
    if closed:
        shutil.rmtree(queue, ignore_errors=True)
    return closed


def shots_command(snapshot, rest):
    return [sys.executable, "-I", str(Path(__file__).resolve().parents[1] / "shots.py"), str(snapshot), *rest]
