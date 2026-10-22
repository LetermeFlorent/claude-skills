import sys

sys.dont_write_bytecode = True
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import ENCODING, guard, refuse
from gitrepo import ensure_exclude, ignored, toplevel, tracked_under
from spec import content_problems, name_problems

HINT = "grep -nE 'TBD|TODO|FIXME' <spec>; echo .ia/ >> .git/info/exclude; git ls-files .ia"


def git_problems(spec):
    root = toplevel(spec.parent)
    if root is None:
        print("git: no repository here, nothing to exclude")
        return []
    if ensure_exclude(root):
        print(f"git: added .ia/ to the exclude file of {root.as_posix()}")
    problems = [f"{path} is tracked by git: a spec is never committed unless the user asks"
                for path in tracked_under(root)]
    if not ignored(root, spec):
        problems.append(f"git does not ignore {spec.name}: a rule re-includes .ia/ or the file is tracked")
    return problems


def main():
    parser = argparse.ArgumentParser(prog="spec_check.py", description="Check a spec written by brainstorming.")
    parser.add_argument("spec", help="<repo>/.ia/specs/YYYY-MM-DD-<topic>-design.md")
    spec = Path(parser.parse_args().spec).resolve()
    if not spec.is_file():
        refuse([f"{spec.as_posix()} does not exist"])
    lines = spec.read_text(encoding=ENCODING).splitlines()
    problems = name_problems(spec) + content_problems(lines) + git_problems(spec)
    if problems:
        refuse(problems)
    print(f"spec ok: {spec.as_posix()}")


if __name__ == "__main__":
    guard(main, HINT)
