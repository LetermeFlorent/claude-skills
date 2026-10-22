import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import guard
from history import describe, profile
from message import ATTRIBUTION
from paths import OK_KIND, classify
from repo import branch, changes, find_root, message, operation, pushed_matching, remote, unpushed
from tools import detect

WIDTH = 4
SHORT = 7


def _attribution(root):
    local = [commit[:SHORT] for commit in unpushed(root) if ATTRIBUTION.search(message(root, commit))]
    if local:
        print(f"attribution: {len(local)} unpushed commits carry one ({', '.join(local)}): run scrub.py")
    pushed = pushed_matching(root, ATTRIBUTION)
    if pushed:
        print(f"attribution: {len(pushed)} pushed commits carry one ({', '.join(pushed)}): tell the user, "
              "never rewrite")


def _changes(root, entries):
    print(f"changes: {len(entries) or 'none'}")
    for entry in entries:
        kind, reason = classify(root, entry)
        moved = f" (from {entry['from']})" if "from" in entry else ""
        verdict = "" if kind == OK_KIND else f"  {kind}: {reason}"
        print(f"  {entry['code']:<{WIDTH}}{entry['path']}{moved}{verdict}")


def main():
    root = find_root(Path.cwd())
    name, upstream = branch(root)
    target = remote(root)
    print(f"repo: {root.as_posix()}")
    print(f"branch: {name or 'detached HEAD'}, upstream: {upstream or 'none'}")
    print(" ".join(filter(None, ("remote:", target["kind"], target["owner"], target["url"]))))
    print(f"unpushed commits: {len(unpushed(root))} (last known state, nothing fetched)")
    busy = operation(root)
    if busy:
        print(f"in progress: {busy}. Stop and ask the user before any commit")
    print("history: " + describe(profile(root)))
    _attribution(root)
    entries = changes(root)
    _changes(root, entries)
    checks = detect(root, [entry["path"] for entry in entries])
    print("quick checks: " + (", ".join(" ".join(command) for _, command in checks) or "none configured"))


if __name__ == "__main__":
    guard(main, "git status --short; git log --oneline -15; git remote -v")
