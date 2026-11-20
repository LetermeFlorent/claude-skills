import argparse
import subprocess
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from blender import FAILED, blender_or_refuse, existing, guard, refuse
from livequeue import QUEUE, close, open_window, running_pid, send, shots_command, wait_for

HINT = "open Blender yourself and paste the script in its Scripting tab"
START_TIMEOUT = 180
SNAPSHOT = "import bpy\nbpy.ops.wm.save_as_mainfile(filepath={!r}, copy=True)\n"


def parse(argv):
    parser = argparse.ArgumentParser(description="Drive a visible Blender window the user watches.")
    parser.add_argument("action", choices=("start", "run", "shots", "status", "stop"))
    parser.add_argument("target", nargs="?", default="", help="start: .blend or nothing; run: script.py")
    parser.add_argument("rest", nargs=argparse.REMAINDER, help="shots: out_dir then shots.py options")
    parser.add_argument("--timeout", type=int, default=900)
    return parser.parse_args(argv)


def start(target):
    if running_pid(QUEUE):
        refuse([f"a live Blender is already open (pid {running_pid(QUEUE)}): use it or stop it first"])
    problems = []
    source = existing(target, problems, "file") if target else ""
    if problems:
        refuse(problems)
    open_window(blender_or_refuse(), source, QUEUE)
    if not wait_for(QUEUE / "ready", START_TIMEOUT):
        print(f"failed: Blender did not open, log: {QUEUE / 'blender.log'}")
        sys.exit(FAILED)
    print(f"live Blender open, pid {running_pid(QUEUE)}")


def step(pid, text, timeout):
    code, output = send(QUEUE, pid, text, timeout)
    if output:
        print(output)
    if code != 0:
        print(f"failed: step exit code {code}")
        sys.exit(FAILED)


def main():
    options = parse(sys.argv[1:])
    if options.action == "start":
        return start(options.target)
    pid = running_pid(QUEUE)
    if options.action == "status":
        return print(f"live Blender open, pid {pid}" if pid else "no live Blender open")
    if not pid:
        refuse(["no live Blender open: run live.py start first"])
    if options.action == "stop":
        return print("closed" if close(QUEUE, pid, 30) else f"failed: pid {pid} still running")
    if options.action == "run":
        problems = []
        script = existing(options.target or "-", problems, "script")
        if problems or script == "-":
            refuse(problems or ["give a script to run"])
        return step(pid, Path(script).read_text(encoding="utf-8"), options.timeout)
    snapshot = QUEUE / "snapshot.blend"
    step(pid, SNAPSHOT.format(str(snapshot)), options.timeout)
    sys.exit(subprocess.run(shots_command(snapshot, [options.target, *options.rest])).returncode)


if __name__ == "__main__":
    guard(main, HINT)
