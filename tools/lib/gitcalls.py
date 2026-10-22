import os
import shutil
import subprocess

TIMEOUT = 20
REMOTE = "origin"
FETCHED = "FETCH_HEAD"
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


def remote_head(repo, branch):
    found = git(repo, "ls-remote", REMOTE, f"refs/heads/{branch}").split()
    if not found:
        raise GitFailed(f"no branch {branch} on {REMOTE}")
    return found[0]


def fetch(repo, branch):
    git(repo, "fetch", "--quiet", REMOTE, branch)


def is_ancestor(repo, old):
    try:
        git(repo, "merge-base", "--is-ancestor", old, FETCHED)
    except GitFailed:
        return False
    return True


def fast_forward(repo):
    git(repo, "merge", "--ff-only", "--quiet", FETCHED)


def changed_paths(repo, old, new):
    return git(repo, "diff", "--name-only", old, new).splitlines()


def top_folders(paths, known):
    return sorted({path.split("/", 1)[0] for path in paths} & set(known))
