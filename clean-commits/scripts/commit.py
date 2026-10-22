import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import ENCODING, FAILED, guard, joined, normalize, read_input, refuse
from history import LANGUAGES, profile
from message import check
from paths import LARGE_KIND, OK_KIND, classify
from repo import changes, find_root, git, operation, read

STDIN = "-"


def _relative(root, raw):
    given = Path(raw)
    return given.resolve().relative_to(root).as_posix() if given.is_absolute() else raw.replace("\\", "/")


def _paths(root, wanted, allow_large):
    known = {entry["path"]: entry for entry in changes(root)}
    known.update({entry["from"]: {**entry, "path": entry["from"]} for entry in list(known.values()) if "from" in entry})
    picked, problems = [], []
    for path in (_relative(root, raw) for raw in wanted):
        entry = known.get(path)
        if entry is None:
            problems.append(f"{path} has no change to commit (list files one by one, not folders)")
            continue
        kind, reason = classify(root, entry)
        if kind != OK_KIND and not (kind == LARGE_KIND and allow_large):
            problems.append(f"{path} is {kind}: {reason}")
        picked.append(entry)
    return picked, problems


def _language(found, given):
    wanted = found["language"] or given
    if not wanted and not found["commits"]:
        return None, ["no history to follow: ask the user the language, then pass --language fr or --language en"]
    return wanted, []


def _commit(root, entries, text):
    new = [entry["path"] for entry in entries if entry["new"]]
    if new:
        git(root, "add", "--", *new)
    code, out, err = git(root, "commit", "-o", "-F", "-", "--", *[entry["path"] for entry in entries], stdin=text)
    if code != 0:
        if new:
            git(root, "reset", "-q", "--", *new)
        print(f"commit failed, nothing committed:\n{joined(out, err)}")
        sys.exit(FAILED)
    print((read(root, "log", "-1", "--format=%h %s") or "").strip())


def main():
    parser = argparse.ArgumentParser(description="Commit the given paths only, after checking them and the message.")
    parser.add_argument("paths", nargs="+", help="every path of this commit, deleted and moved ones included")
    parser.add_argument("--message-file", default=STDIN, help="file holding the message, - for stdin (default)")
    parser.add_argument("--language", choices=LANGUAGES, help="language the user chose, when there is no history")
    parser.add_argument("--allow-large", action="store_true", help="the user agreed to commit a large new file")
    args = parser.parse_args()
    root = find_root(Path.cwd())
    given = Path(args.message_file)
    text = read_input() if args.message_file == STDIN else normalize(given.read_text(encoding=ENCODING))
    busy = operation(root)
    found = profile(root)
    wanted, problems = _language(found, args.language)
    entries, path_problems = _paths(root, args.paths, args.allow_large)
    problems += path_problems + check(text, found, wanted)
    problems += [f"a {busy} is in progress: ask the user"] if busy else []
    if problems:
        refuse(problems)
    _commit(root, entries, text)
    left = len(changes(root))
    print(f"left uncommitted: {left} paths" if left else "working tree clean")


if __name__ == "__main__":
    guard(main, 'git add -- <new files>; git commit -o -F <message file> -- <paths>')
