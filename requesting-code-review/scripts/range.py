import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from attribution import branch_hit, findings
from gitrange import GitError, branch_name, changed_files, commits, default_base, find_root, resolve

REFUSED, FAILED = 2, 1
HINT = 'git diff --stat <base>..<head> and git log <base>..<head> by hand'
SHORT = 7


def fail(message):
    print(f"range: {message}")
    print(f"by hand: {HINT}")
    sys.exit(FAILED)


def refuse(*reasons):
    print("range: refused")
    for reason in reasons:
        print(f"  {reason}")
    sys.exit(REFUSED)


def resolve_range(root, args):
    head = resolve(root, args.head)
    if not head:
        refuse(f"head {args.head} is not a commit of this repository")
    if args.base:
        base, how = resolve(root, args.base), "given"
        if not base:
            refuse(f"base {args.base} is not a commit of this repository")
        return base, head, how
    base, how = default_base(root, head)
    if not base:
        refuse("no base found: give --base <sha>")
    return base, head, how


def report(root, base, head, how):
    rows = commits(root, base, head)
    files = changed_files(root, base, head)
    if not rows or not files:
        refuse(f"nothing between {base[:SHORT]} and {head[:SHORT]}: no commit or no file changed")
    print(f"repo: {root}")
    print(f"base: {base} ({how})")
    print(f"head: {head}")
    print(f"commits: {len(rows)}")
    for row in rows:
        print(f"  {row['sha'][:SHORT]} {row['subject']}")
    print(f"files: {len(files)}")
    for status, path in files:
        print(f"  {status} {path}")
    branch = branch_name(root)
    hits = findings(rows) + ([f"branch name: {branch}"] if branch_hit(branch) else [])
    print(f"attribution: {len(hits) or 'none'}")
    for hit in hits:
        print(f"  {hit}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Resolve the range of a review, read only.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args()
    root = find_root(args.repo)
    if not root:
        refuse(f"{args.repo} is not inside a git repository")
    try:
        report(root, *resolve_range(root, args))
    except GitError as error:
        fail(error)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        fail(f"{type(error).__name__}: {error}")
