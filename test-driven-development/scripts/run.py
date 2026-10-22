import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from commands import BUILDERS, build
from common import FAILED, GREEN, PASSED, RED, REFUSED, guard
from detect import find_root, runners
from outcome import judge, parse
from process import execute, resources

HINT = ("run the project's own test command at below normal priority, without watch mode, with at most "
        "2 workers, and read its summary")
END_OF_OPTIONS = "--"
CUSTOM = "custom"
TIMEOUT = 600
TAIL = 60
WORKERS = 2
LOW_WORKERS = 1
MIN_FREE_MB = 1500
MAX_CPU = 85
MIN_DISK_GB = 20
SHOWN_NAMES = 10


def _arguments():
    argv = sys.argv[1:]
    cut = argv.index(END_OF_OPTIONS) if END_OF_OPTIONS in argv else len(argv)
    parser = argparse.ArgumentParser(description="Run one test, one file or the suite, and check the red or green.")
    parser.add_argument("target", nargs="?", help="FILE or FILE::NAME, relative to the project root")
    parser.add_argument("--expect", required=True, choices=(RED, GREEN))
    parser.add_argument("--suite", action="store_true", help="run the whole suite")
    parser.add_argument("--runner", choices=sorted(BUILDERS))
    parser.add_argument("--timeout", type=int, default=TIMEOUT, help="seconds before the process tree is stopped")
    parser.add_argument("--tail", type=int, default=TAIL, help="output lines shown")
    parser.add_argument("--full", action="store_true", help="show the whole output")
    args = parser.parse_args(argv[:cut])
    args.custom = argv[cut + 1:]
    return args


def _scope_problems(args):
    if args.custom or bool(args.target) != args.suite:
        return []
    return ["name one test or one file, or pass --suite, never both"]


def _workers(root, suite):
    if not suite:
        return WORKERS
    found = resources(root)
    if found is None:
        print("resources: unreadable, one worker")
        return LOW_WORKERS
    free_mb, cpu, disk_gb = found
    print(f"resources: {free_mb:.0f} MB free, CPU {cpu:.0f} %, {disk_gb:.0f} GB free on {root.drive or 'disk'}")
    if disk_gb < MIN_DISK_GB:
        print(f"disk under {MIN_DISK_GB} GB: free space before going on")
    if free_mb < MIN_FREE_MB or cpu > MAX_CPU:
        print(f"under {MIN_FREE_MB} MB free or over {MAX_CPU} % CPU: one worker")
        return LOW_WORKERS
    return WORKERS


def _command(args, root, workers):
    if args.custom:
        return CUSTOM, args.custom, {}
    found = [args.runner] if args.runner else runners(root, args.target)
    if not found:
        raise LookupError("no test runner found here: pass --runner, or the command after --")
    if len(found) > 1:
        print(f"also in this project: {', '.join(found[1:])}; its suite is part of the project's suite too")
    command, env = build(found[0], root, args.target, workers)
    return found[0], command, env


def _show(output, args, outcome, code):
    lines = output.rstrip().splitlines()
    shown = lines if args.full or len(lines) <= args.tail else lines[-args.tail:]
    print(f"output, {'all' if shown is lines else f'last {len(shown)} of {len(lines)}'} lines:")
    print("\n".join(shown))
    print(f"exit code: {code}")
    if outcome.ran is not None:
        print(f"counts: {outcome.ran} ran, {outcome.failed} failed, {outcome.errors} error(s)")
    for name in outcome.names[:SHOWN_NAMES]:
        print(f"failing: {name}")
    if outcome.reason:
        print(f"first error line: {outcome.reason}")


def main():
    args = _arguments()
    problems = _scope_problems(args)
    if problems:
        print(f"refused: {problems[0]}")
        return REFUSED
    root = find_root(Path.cwd())
    workers = _workers(root, args.suite)
    runner, command, env = _command(args, root, workers)
    print(f"runner: {runner}, root: {root.as_posix()}")
    print(f"running: {' '.join(command)} (below normal priority, timeout {args.timeout} s)")
    code, output = execute(command, root, env, args.timeout)
    if code is None:
        print("\n".join(output.rstrip().splitlines()[-args.tail:]))
        print(f"failed: still running after {args.timeout} s, the process tree was stopped")
        return FAILED
    outcome = parse(runner, output, code)
    _show(output, args, outcome, code)
    ok, verdict = judge(args.expect, outcome, code)
    for line in verdict:
        print(line if ok else f"refused: {line}")
    return PASSED if ok else REFUSED


if __name__ == "__main__":
    guard(main, HINT)
