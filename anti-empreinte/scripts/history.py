import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import DECODE_ERRORS, ENCODING, FAILED, guard, refuse
from gitlog import current_branch, dirty, drop_backup, find_root, history, message, rewrite, unpushed
from signatures import TRAILER

LF, CRLF = "\n", "\r\n"


def clean(text):
    kept = [line for line in text.replace(CRLF, LF).splitlines() if not TRAILER.search(line)]
    while kept and not kept[-1].strip():
        kept.pop()
    return LF.join(kept) + LF


def _marked(root):
    return [commit for commit in unpushed(root) if TRAILER.search(message(root, commit))]


def _filter():
    text = sys.stdin.buffer.read().decode(ENCODING, errors=DECODE_ERRORS)
    sys.stdout.flush()
    sys.stdout.buffer.write(clean(text).encode(ENCODING))


def _fix(root):
    name = current_branch(root)
    marked = _marked(root)
    if not marked:
        print("no unpushed commit of this branch carries an attribution")
        return
    if not name or dirty(root):
        refuse(["the rewrite needs a branch and no change to tracked files; those changes may be another "
                "session's work: never stash them, ask the user"])
    command = f'"{Path(sys.executable).as_posix()}" -I "{Path(__file__).resolve().as_posix()}" --filter'
    code, out, err = rewrite(root, command)
    if code != 0:
        print(f"filter-branch failed, history unchanged:\n{(out + err).strip()}")
        sys.exit(FAILED)
    drop_backup(root, name)
    left = _marked(root)
    print(f"attribution left in {len(left)} unpushed commits" if left else
          f"attribution removed from {len(marked)} unpushed commits of {name}, author and pushed history untouched")
    others = history(root)[0]["local"]
    if others:
        print(f"other local branches still hold signed commits: {' '.join(others)}")


def _report(root):
    signed, bots = history(root)
    print(f"signed commits not pushed: {len(signed['local'])} {' '.join(signed['local'])}".rstrip())
    print(f"signed commits already pushed: {len(signed['pushed'])} {' '.join(signed['pushed'])}".rstrip())
    for row in bots:
        print(f"bot identity, left as is: {row}")


def main():
    parser = argparse.ArgumentParser(description="Find, and with --fix remove, AI attribution in git messages.")
    parser.add_argument("--fix", action="store_true", help="rewrite the unpushed commits of this branch")
    parser.add_argument("--filter", action="store_true", help="message filter used by filter-branch")
    args = parser.parse_args()
    if args.filter:
        _filter()
        return
    root = find_root(Path.cwd())
    if root is None:
        refuse([f"{Path.cwd()} is not inside a git repository"])
    if args.fix:
        _fix(root)
    else:
        _report(root)


if __name__ == "__main__":
    guard(main, "git filter-branch --msg-filter on HEAD --not --remotes only, then git log --all --grep")
