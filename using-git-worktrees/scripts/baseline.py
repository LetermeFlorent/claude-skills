import argparse
import os
import subprocess
import sys
import tempfile
from collections import namedtuple

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

import commands
import gitinfo
import resources
from common import FAILED, LOW_PRIORITY, guard, refuse

TOOL = "using-git-worktrees"
LOG_FOLDER = ("claude-skills", "worktree-baseline")
DEFAULT_TIMEOUT = 540
INSTALL_TIMEOUT = 540
TAIL_LINES = 15
Place = namedtuple("Place", "cwd log env")


def log_path(worktree):
    folder = Path(tempfile.gettempdir()).joinpath(*LOG_FOLDER)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / (worktree.name + ".log")


def run_logged(command, place, timeout):
    with open(place.log, "a", encoding="utf-8", errors="replace") as handle:
        handle.write("$ " + " ".join(command) + "\n")
        handle.flush()
        process = subprocess.Popen(command, cwd=str(place.cwd), stdout=handle, stderr=subprocess.STDOUT,
                                   env={**os.environ, **place.env}, creationflags=LOW_PRIORITY, shell=os.name == "nt")
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(process.pid)], capture_output=True)
            handle.write(f"timed out after {timeout} s\n")
            return None


def tail(log):
    lines = Path(log).read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-TAIL_LINES:])


def finish(code, log):
    print(tail(log))
    if code == 0:
        print(f"BASELINE DONE exit=0 log={Path(log).as_posix()}")
        return
    print(f"BASELINE FAILED exit={code} log={Path(log).as_posix()}")
    sys.exit(FAILED)


def main():
    parser = argparse.ArgumentParser(prog="baseline.py")
    parser.add_argument("worktree")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    worktree = Path(args.worktree).resolve()
    main_root = gitinfo.git_dirs(worktree)[1].parent
    seen = resources.probe(worktree)
    if seen is None:
        print("resources: could not be read, using one worker")
    workers = resources.workers_for(seen["free_mb"], seen["cpu"]) if seen else 1
    if seen:
        print(f"resources: {seen['free_mb']} MB free, cpu {seen['cpu']} %, disk {seen['disk_gb']} GB free")
    if workers == 0:
        refuse([f"only {seen['free_mb']} MB free, under {resources.MIN_FREE_MB}: wait for memory, do not stack"])
    log = log_path(worktree)
    log.write_text("", encoding="utf-8")
    env = commands.extra_env(main_root, resources.heap_mb(seen["free_mb"] if seen else resources.MIN_FREE_MB))
    place = Place(worktree, log, env)
    install = commands.install_command(worktree)
    if install and run_logged(install, place, INSTALL_TIMEOUT) != 0:
        finish(None, log)
    test = commands.test_command(worktree, workers)
    if test is None:
        print("BASELINE SKIPPED no test command found")
        return
    finish(run_logged(test, place, args.timeout), log)


if __name__ == "__main__":
    guard(TOOL, main, "run the project's test command inside the worktree at low priority, 2 workers at most")
