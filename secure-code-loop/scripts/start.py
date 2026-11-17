import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent / "lib"))

import project
import tools
from common import LEDGERS, START_FILE, guard, new_work, refuse, write_json
from findings import relative_path

HINT = f'python -I "{HERE.as_posix()}" --root "<project>"'
STACK_LIMIT = 20
SHORT_COMMIT = 12
WHOLE = "."


def arguments():
    parser = argparse.ArgumentParser(description="Record the project state before the loop and list the scanners.")
    parser.add_argument("--root", default=WHOLE, help="project folder, the current one by default")
    chosen = parser.add_mutually_exclusive_group()
    chosen.add_argument("--base", help="scope: files changed since this git revision, plus files touched later")
    chosen.add_argument("--scope", nargs="+", help="scope: these files or folders, plus files touched later")
    return parser.parse_args()


def scope_of(options, root, is_git):
    if options.base:
        commit = project.commit_of(root, options.base) if is_git else None
        if not commit:
            refuse([f"{options.base} is not a commit of {root}" if is_git else "--base needs a git project"])
        return {"base": commit, "revision": options.base}
    paths = [relative_path(path, root).rstrip("/") for path in options.scope or []]
    if not paths or WHOLE in paths:
        return {}
    missing = [path for path in paths if not (root / path).exists()]
    if missing:
        refuse([f"{path} is not in {root.as_posix()}" for path in missing])
    return {"paths": paths}


def inventory(names, is_git):
    return [f"tool: {tool.name} " + ("not needed" if not tool.places(names, is_git) else
                                     "ready" if tools.installed(tool) else tools.MISSING) for tool in tools.TOOLS]


def stack(names):
    found = [name for name in names if tools.is_manifest(name)]
    return found[:STACK_LIMIT] + ([f"and {len(found) - STACK_LIMIT} more"] if len(found) > STACK_LIMIT else [])


def describe(scope):
    if scope.get("base"):
        return f"files changed since {scope['revision']} ({scope['base'][:SHORT_COMMIT]}), plus files touched later"
    if scope.get("paths"):
        return f"{', '.join(scope['paths'])}, plus files touched later"
    return "whole project"


def show(work, start, names):
    print(f"work: {work.as_posix()}")
    print(f"root: {start['root']}, {'git' if start['is_git'] else 'not git'}, {len(names)} files, "
          f"{len(start['dirty'])} uncommitted (never restored by finish)")
    print(f"scope: {describe(start['scope'])}")
    for name in LEDGERS:
        print(f"ledger: {(work / name).as_posix()}")
    for line in inventory(names, start["is_git"]):
        print(line)
    for name in stack(names):
        print(f"stack: {name}")
    ready = [{"tool": tool.name, "state": tools.OK} for tool in tools.TOOLS
             if tools.installed(tool) and tool.places(names, start["is_git"])]
    gaps = tools.not_covered(ready, names)
    if gaps:
        print(f"not covered: {', '.join(gaps)}")
    for name in names:
        if project.TEMPORARY.search(name):
            print(f"old temporary: {name}")


def main():
    options = arguments()
    if not Path(options.root).is_dir():
        refuse([f"{options.root} is not a folder"])
    root, is_git = project.root_of(options.root)
    scope = scope_of(options, root, is_git)
    names = project.files(root, is_git)
    start = {"root": root.as_posix(), "is_git": is_git, "scope": scope, **project.snapshot(root, is_git, names)}
    work = new_work()
    write_json(work / START_FILE, start)
    show(work, start, names)


if __name__ == "__main__":
    guard(main, HINT)
