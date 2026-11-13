from pathlib import Path

from common import ENCODING, DECODE_ERRORS, run
from signatures import AI_ACTIONS, AI_BRANCH, AI_FILES, BOT_IDENTITY, TRAILER

GIT = "git"
FIELD, RECORD = "\x1f", "\x1e"
LOG_FORMAT = f"--format=%H{FIELD}%an{FIELD}%ae{FIELD}%cn{FIELD}%ce{FIELD}%B{RECORD}"
UNPUSHED = ("HEAD", "--not", "--remotes")
WORKFLOWS = ".github/workflows/"
SHORT = 8


class GitError(Exception):
    pass


def read(root, *args):
    code, out, _ = run([GIT, *args], root)
    return out if code == 0 else None


def need(root, *args):
    code, out, err = run([GIT, *args], root)
    if code != 0:
        raise GitError(f"history not read: git {args[0]}: {err.strip() or f'exit {code}'}")
    return out


def find_root(start):
    folder = start if start.is_dir() else start.parent
    top = read(folder, "rev-parse", "--show-toplevel")
    return Path(top.strip()).resolve() if top else None


def _commits(root):
    for record in need(root, "log", "--all", LOG_FORMAT).split(RECORD):
        parts = record.strip("\n").split(FIELD)
        if len(parts) == 6:
            yield parts


def unpushed(root):
    return set((read(root, "rev-list", *UNPUSHED) or "").split())


def pushed(root):
    return set(need(root, "rev-list", "--remotes").split())


def history(root):
    remote = pushed(root)
    signed, bots = {"pushed": [], "local": []}, []
    for sha, author, email, committer, committer_email, body in _commits(root):
        place = "pushed" if sha in remote else "local"
        if TRAILER.search(body):
            signed[place].append(sha[:SHORT])
        identity = " ".join((author, email, committer, committer_email))
        if BOT_IDENTITY.search(identity):
            bots.append(f"{sha[:SHORT]} {author} <{email}>")
    return signed, bots


def branches(root):
    names = (read(root, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes") or "").split()
    return [name for name in names if AI_BRANCH.search(name)]


def tracked(root):
    files = (read(root, "ls-files") or "").splitlines()
    flagged = [name for name in files if AI_FILES.search(name)]
    for name in files:
        if name.startswith(WORKFLOWS) and _uses_ai_action(root / name):
            flagged.append(name)
    return flagged


def _uses_ai_action(path):
    try:
        return bool(AI_ACTIONS.search(path.read_text(encoding=ENCODING, errors=DECODE_ERRORS)))
    except OSError:
        return False


def message(root, commit):
    return read(root, "log", "-1", "--format=%B", commit) or ""


def current_branch(root):
    return (read(root, "branch", "--show-current") or "").strip()


def dirty(root):
    return bool((read(root, "status", "--porcelain", "--untracked-files=no") or "").strip())


def rewrite(root, filter_command):
    return run([GIT, "filter-branch", "-f", "--msg-filter", filter_command, "--", *UNPUSHED], root)


def drop_backup(root, name):
    run([GIT, "update-ref", "-d", f"refs/original/refs/heads/{name}"], root)


def findings(root):
    try:
        (signed, bots), hand = history(root), []
    except GitError as error:
        signed, bots, hand = {"local": [], "pushed": []}, [], [(root, str(error))]
    local, remote = signed["local"], signed["pushed"]
    if local:
        hand.append((root, f"signed commits not pushed ({len(local)}): {', '.join(local)}"))
    flags = [(root, f"signed commits already pushed ({len(remote)}): {', '.join(remote)}")] if remote else []
    flags += [(root, f"commit by a bot identity {row}") for row in bots]
    flags += [(root, f"branch named after an AI tool: {name}") for name in branches(root)]
    return hand, flags + [(root / name, "tracked AI tool file") for name in tracked(root)]
