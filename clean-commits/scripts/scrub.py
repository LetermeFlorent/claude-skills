import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import FAILED, guard, joined, read_input, refuse, write_output
from message import ATTRIBUTION
from repo import UNPUSHED, branch, find_root, git, message, read, unpushed

ORIGINAL = "refs/original/refs/heads/"


def _clean(text):
    kept = [line for line in text.splitlines() if not ATTRIBUTION.search(line)]
    while kept and not kept[-1].strip():
        kept.pop()
    return "\n".join(kept) + "\n"


def _marked(root):
    return [commit for commit in unpushed(root) if ATTRIBUTION.search(message(root, commit))]


def _rewrite(root, name):
    command = f'"{Path(sys.executable).as_posix()}" -I "{Path(__file__).resolve().as_posix()}" --filter'
    code, out, err = git(root, "filter-branch", "-f", "--msg-filter", command, "--", *UNPUSHED)
    if code != 0:
        print(f"filter-branch failed, history unchanged:\n{joined(out, err)}")
        sys.exit(FAILED)
    git(root, "update-ref", "-d", ORIGINAL + name)


def main():
    parser = argparse.ArgumentParser(description="Remove AI tool attribution from unpushed commits.")
    parser.add_argument("--filter", action="store_true", help="message filter used by filter-branch")
    args = parser.parse_args()
    if args.filter:
        write_output(_clean(read_input()))
        return
    root = find_root(Path.cwd())
    name, _ = branch(root)
    marked = _marked(root)
    if not marked:
        print("no unpushed commit carries an attribution")
        return
    dirty = read(root, "status", "--porcelain", "--untracked-files=no")
    if not name or dirty:
        refuse(["the rewrite needs a branch and no change to tracked files; those changes may be another "
                "session's work: never stash them, ask the user"])
    _rewrite(root, name)
    left = _marked(root)
    print(f"attribution left in {len(left)} unpushed commits" if left else
          f"attribution removed from {len(marked)} unpushed commits, pushed history untouched")


if __name__ == "__main__":
    guard(main, "git filter-branch --msg-filter on the unpushed range only, then check git log")
