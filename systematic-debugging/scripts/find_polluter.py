import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import guard, refuse, run
from polluter import bisect, clean_path, collect, expand

DEFAULT_TIMEOUT = 300
SAMPLE_FILE = "sample"
HINT = "run your test command on one test file at a time and look for the leftover after each run"


def parse(argv):
    parser = argparse.ArgumentParser(prog="find_polluter", description="Find the test file that pollutes the others.")
    parser.add_argument("--tests", required=True, help='test files from the current folder: "tests/**/test_*.py"')
    parser.add_argument("--run", required=True, help='test command, {} marks the files: "python -m pytest -q {}"')
    goal = parser.add_mutually_exclusive_group(required=True)
    goal.add_argument("--creates", help="a file or folder no test should leave behind")
    goal.add_argument("--breaks", help="a test file that passes alone and fails after the others")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="seconds allowed for one run")
    return parser.parse_args(argv)


def problems_of(args, root, files):
    problems = []
    if expand(args.run, [SAMPLE_FILE]) is None:
        problems.append(f"--run needs a {{}} where the test files go: {args.run}")
    if not files:
        problems.append(f"no test file matches {args.tests} under {root.as_posix()}")
    if args.creates and (root / args.creates).exists():
        problems.append(f"{args.creates} already exists: move it out of the way, then run again")
    if args.breaks and not (root / args.breaks).is_file():
        problems.append(f"{args.breaks} is not a file under {root.as_posix()}")
    return problems


def hunt_creator(args, root, files):
    target = root / args.creates
    total = len(files)
    for count, test in enumerate(files, start=1):
        run(expand(args.run, [test]), root, args.timeout)
        if target.exists():
            print(f"[{count}/{total}] {test}: left {args.creates}")
            print(f"polluter: {test}")
            return
        print(f"[{count}/{total}] {test}: clean")
    print(f"no polluter: {total} files run, none left {args.creates}")


def hunt_breaker(args, root, files):
    victim = clean_path(args.breaks)
    candidates = [test for test in files if test != victim]

    def fails(group):
        failed = run(expand(args.run, [*group, victim]), root, args.timeout) != 0
        print(f"{len(group)} files then {victim}: {'fails' if failed else 'passes'}")
        return failed

    if fails([]):
        refuse([f"{victim} fails on its own: debug it directly, the order is not the cause"])
    if not fails(candidates):
        refuse([f"{victim} passes after all {len(candidates)} files: the suite runs them in another order or setup"])
    suspects, single = bisect(candidates, fails)
    print(f"polluter: {suspects[0]}" if single else f"polluters together: {', '.join(suspects)}")


def main():
    args = parse(sys.argv[1:])
    root = Path.cwd()
    files = collect(root, args.tests)
    problems = problems_of(args, root, files)
    if problems:
        refuse(problems)
    hunt = hunt_creator if args.creates else hunt_breaker
    hunt(args, root, files)


if __name__ == "__main__":
    guard(main, HINT)
