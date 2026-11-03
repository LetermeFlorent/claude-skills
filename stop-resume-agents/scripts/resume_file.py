import argparse
import datetime
import glob
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from common import MARKER, config_dir, guard

NAMES = ("resume.md", "resume-stop-all.md")
HINT = "Do the same step by hand."


def journal_path():
    return os.path.join(config_dir(), "stop-resume", "journal.tsv")


def all_journals():
    home = os.path.expanduser("~")
    paths = {journal_path()} | set(glob.glob(os.path.join(home, ".claude*", "stop-resume", "journal.tsv")))
    return [p for p in paths if os.path.isfile(p)]


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def git_root(start):
    try:
        out = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def candidate_dirs(start):
    home = os.path.expanduser("~")
    roots = [folder for folder in (git_root(start), start) if folder]
    dirs = [os.path.join(folder, ".ia") for folder in roots] + roots
    for journal in all_journals():
        for line in read_text(journal).splitlines()[-200:]:
            fields = line.split("\t")
            if len(fields) == 4:
                dirs.append(os.path.dirname(fields[3]))
    dirs += [os.path.join(home, sub) for sub in ("Desktop", "OneDrive/Desktop", "OneDrive/Bureau")]
    seen, result = set(), []
    for folder in dirs:
        key = os.path.normcase(os.path.abspath(folder))
        if key not in seen and os.path.isdir(folder):
            seen.add(key)
            result.append(folder)
    return result


def describe(text):
    state = next((l for l in text.splitlines() if l.startswith("Etat :")), "Etat : inconnu")
    origin = next(iter(re.findall(r"session d'origine (\S+?)\.?$", text, re.M)), "inconnue")
    return state, origin


def scan(folder):
    ours, foreign = [], []
    paths = {os.path.join(folder, n) for n in NAMES} | set(glob.glob(os.path.join(folder, "resume-*.md")))
    for path in sorted(p for p in paths if os.path.isfile(p)):
        text = read_text(path)
        if text.startswith(MARKER):
            ours.append((os.path.getmtime(path), path) + describe(text))
        else:
            foreign.append(path)
    return ours, foreign


def find(start):
    ours, foreign = [], []
    for folder in candidate_dirs(start):
        found, other = scan(folder)
        ours += found
        foreign += other
    for mtime, path, state, origin in sorted(ours, reverse=True):
        stamp = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        print(f"{stamp}\t{state}\tsession {origin}\t{os.path.normpath(path)}")
    if not ours:
        print("no resume file written by /stop-all was found: ask the user for its path")
    for path in foreign:
        print(f"not ours, leave untouched: {os.path.normpath(path)}")


def digest(paths):
    for path in paths:
        try:
            with open(path, "rb") as handle:
                print(f"{hashlib.sha256(handle.read()).hexdigest()[:12]}  {os.path.normpath(path)}")
        except OSError:
            print(f"missing       {os.path.normpath(path)}")


def log(path, event):
    os.makedirs(os.path.dirname(journal_path()), exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    session = os.environ.get("CLAUDE_CODE_SESSION_ID", "unknown")
    with open(journal_path(), "a", encoding="utf-8") as handle:
        handle.write(f"{stamp}\t{session}\t{event}\t{os.path.abspath(path)}\n")
    print(f"logged {event} for {os.path.abspath(path)}")


def main():
    parser = argparse.ArgumentParser(description="Find and log the resume files written by /stop-all.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("find")
    logger = sub.add_parser("log")
    logger.add_argument("path")
    logger.add_argument("event", choices=["stop", "resume"])
    sub.add_parser("hash").add_argument("paths", nargs="+")
    args = parser.parse_args()
    if args.command == "find":
        find(os.getcwd())
    elif args.command == "hash":
        digest(args.paths)
    else:
        log(args.path, args.event)


if __name__ == "__main__":
    guard(main, HINT)
