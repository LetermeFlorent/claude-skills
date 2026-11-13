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
from common import FAILED, LOW_PRIORITY, guard, refuse, run

TOOL = "using-git-worktrees"
LOG_FOLDER = ("claude-skills", "worktree-baseline")
TIMEOUT = 540
LIST_TIMEOUT = 120
INSTALL, TESTS = "install", "tests"
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


def status(code, step):
    if code == 0:
        return "BASELINE DONE exit=0"
    if code is None:
        return f"BASELINE TIMED OUT after {TIMEOUT} s ({step})"
    return f"BASELINE INSTALL FAILED exit={code}" if step == INSTALL else f"BASELINE FAILED exit={code}"


def finish(code, log, step=TESTS):
    print(tail(log))
    print(f"{status(code, step)} log={Path(log).as_posix()}")
    if code != 0:
        sys.exit(FAILED)


def runner_check(main_root, worktree):
    if not worktree.is_relative_to(main_root):
        return "runner check: the worktree is outside the repository, no runner of the main checkout reads it"
    command = commands.list_command(main_root)
    if not command:
        return "runner check: no list mode for this test runner, check the runner hints by hand"
    code, out, err = run(command, main_root, LIST_TIMEOUT)
    shown = " ".join(command)
    if code is None:
        return f"runner check: could not run {shown}: {err}"
    if commands.reads_worktree(out + err, worktree, main_root):
        return f"runner check: {shown} lists worktree files: show the runner hints, edit config only if the user agrees"
    if code not in (0, 5):
        return f"runner check: {shown} failed (exit {code}), check the runner hints by hand"
    return f"runner check: {shown} does not read the worktree"


def main():
    parser = argparse.ArgumentParser(prog="baseline.py")
    parser.add_argument("worktree")
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
    if install:
        done = run_logged(install, place, TIMEOUT)
        if done != 0:
            finish(done, log, INSTALL)
    print(runner_check(main_root, worktree))
    test = commands.test_command(worktree, workers)
    if test is None:
        print("BASELINE SKIPPED no test command found")
        return
    finish(run_logged(test, place, TIMEOUT), log)


if __name__ == "__main__":
    guard(TOOL, main, "run the project's test command inside the worktree at low priority, 2 workers at most")
