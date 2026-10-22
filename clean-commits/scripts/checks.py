import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import REFUSED, guard, joined, run
from repo import find_root
from tools import detect

CHECK_TIMEOUT = 300
SHOWN = 15


def _mentions(output, root, paths):
    names = {path.replace("\\", "/") for path in paths}
    names |= {(root / path).as_posix() for path in names}
    lines = output.replace("\\", "/").splitlines()
    return [line for line in lines if any(name in line for name in names)]


def _report(name, command, outcome):
    print(f"{name}: {' '.join(command)}")
    for line in outcome[:SHOWN]:
        print(f"  {line}")


def main():
    parser = argparse.ArgumentParser(description="Run the project's quick checks for the files of one commit.")
    parser.add_argument("paths", nargs="+", help="the commit's paths, from the repository root")
    args = parser.parse_args()
    root = find_root(Path.cwd())
    found, blocked = detect(root, args.paths), False
    if not found:
        print("no quick check configured for these files")
    for name, command in found:
        code, out, err = run(command, root, CHECK_TIMEOUT)
        output = joined(out, err)
        mentioned = _mentions(output, root, args.paths) if code else []
        if code == 0:
            _report(f"{name} passed", command, [])
        elif code is None:
            _report(f"{name} could not run", command, [output])
        elif mentioned:
            blocked = True
            _report(f"{name} FAILED on these files, do not commit them", command, mentioned)
        else:
            _report(f"{name} fails on other files only, commit allowed, tell the user", command, output.splitlines())
    sys.exit(REFUSED if blocked else 0)


if __name__ == "__main__":
    guard(main, "run the project's lint and typecheck scripts through its package manager")
