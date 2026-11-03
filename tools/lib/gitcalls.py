import os
import re
import shutil
import subprocess

TIMEOUT = 20
REMOTE = "origin"
TAG_PREFIX = "v"
PEELED = "^{}"
VERSION = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
NO_PROMPT = ("-c", "credential.helper=")
QUIET_ENV = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}


class GitMissing(Exception):
    pass


class GitFailed(Exception):
    pass


def git(repo, *args):
    if shutil.which("git") is None:
        raise GitMissing("git not found")
    command = ["git", *NO_PROMPT, "-C", str(repo), *args]
    try:
        done = subprocess.run(command, capture_output=True, text=True, errors="replace", timeout=TIMEOUT,
                              env={**os.environ, **QUIET_ENV})
    except subprocess.TimeoutExpired as error:
        raise GitFailed(f"git {args[0]} gave no answer in {TIMEOUT} s") from error
    if done.returncode != 0:
        raise GitFailed(done.stderr.strip() or f"git {args[0]} failed")
    return done.stdout.strip()


def head(repo):
    return git(repo, "rev-parse", "HEAD")


def is_dirty(repo):
    return bool(git(repo, "status", "--porcelain", "--untracked-files=no"))


def latest_release(repo):
    found = {}
    for line in git(repo, "ls-remote", "--tags", REMOTE, f"{TAG_PREFIX}*").splitlines():
        sha, _, ref = line.partition("	")
        name = ref.removeprefix("refs/tags/")
        peeled = name.endswith(PEELED)
        name = name.removesuffix(PEELED)
        number = version(name)
        if number is not None and (peeled or name not in found):
            found[name] = (number, sha)
    if not found:
        return None
    name = max(found, key=lambda tag: found[tag][0])
    return name, found[name][1]


def version(tag):
    match = VERSION.fullmatch(tag)
    return tuple(int(part) for part in match.groups()) if match else None


def fetch_tag(repo, tag):
    git(repo, "fetch", "--quiet", "--no-tags", REMOTE, f"refs/tags/{tag}:refs/tags/{tag}")


def is_ancestor(repo, older, newer):
    try:
        git(repo, "merge-base", "--is-ancestor", older, newer)
    except GitFailed:
        return False
    return True


def fast_forward(repo, commit):
    git(repo, "merge", "--ff-only", "--quiet", commit)


def current_release(repo):
    try:
        return git(repo, "describe", "--tags", "--abbrev=0", "--match", f"{TAG_PREFIX}*")
    except GitFailed:
        return ""


def changed_paths(repo, old, new):
    return git(repo, "diff", "--name-only", old, new).splitlines()
