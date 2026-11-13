import re
import sys
import time

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from gitcalls import (GitFailed, GitMissing, changed_paths, current_release, fast_forward, fetch_tag, head,
                      is_ancestor, is_dirty, latest_release)
from board import sync_board
from caveman import sync_caveman
from graphify import start_background
from guard import run_guarded
from hook import add_hooks
from paths import CAVEMAN_FILE, GRAPHIFY_FILE, INSTALLED_FILE, PONYTAIL_FILE, config_dir, repo_dir, skill_names, state_file
from ponytail import LABEL, checkout_dir, force_mode, mode_file, sync_ponytail
from registry import read_json, write_json
from sync import sync

PREFIX = "claude-skills"
DONE = 0
HINT = 'by hand: git -C "<config>/claude-skills" pull --ff-only, then run tools/install.py, see INSTALL.md'
CHECK_FILE = "update-check.stamp"
CHECK_SECONDS = 6 * 3600
QUIET = re.compile(r"(.+: )?up to date \(.+\)|.+(already there|already running, starts at every login)")


def resync(repo):
    registry_path = state_file(repo, INSTALLED_FILE)
    registry, lines = sync(repo, repo.parent, read_json(registry_path))
    write_json(registry_path, registry)
    return [text for _, text in lines]


def changed_skills(repo, old, new, before):
    known = set(before) | set(skill_names(repo))
    return sorted({path.split("/", 1)[0] for path in changed_paths(repo, old, new)} & known)


def check(repo):
    if is_dirty(repo):
        return ["local changes: not updated"]
    try:
        latest = latest_release(repo)
    except GitFailed:
        return ["could not reach GitHub: kept the installed version"]
    if latest is None:
        return ["no release published yet"]
    tag, _ = latest
    old = head(repo)
    try:
        fetch_tag(repo, tag)
    except GitFailed:
        return [f"could not fetch {tag}: kept the installed version"]
    if is_ancestor(repo, tag, old):
        return [f"up to date ({current_release(repo) or tag})"]
    if not is_ancestor(repo, old, tag):
        return [f"local commits: {tag} not installed"]
    was, before = current_release(repo) or old[:7], skill_names(repo)
    try:
        fast_forward(repo, f"{tag}^{{commit}}")
    except GitFailed as error:
        return [f"could not install {tag}: {error}"]
    names = changed_skills(repo, old, head(repo), before)
    return [f"updated {was} to {tag}: {', '.join(names) or 'tools only'}"]


def network_due(stamp, now=None):
    now = time.time() if now is None else now
    if stamp.is_file() and 0 <= now - stamp.stat().st_mtime < CHECK_SECONDS:
        return False
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.touch()
    return True


def checked(repo):
    try:
        return check(repo)
    except GitMissing:
        return ["git not found: update skipped"]
    except GitFailed as error:
        return [f"update stopped: {error}"]


def online(repo):
    lines = checked(repo)
    found = sync_ponytail(repo.parent, state_file(repo, PONYTAIL_FILE))
    found += sync_caveman(repo.parent, state_file(repo, CAVEMAN_FILE)) + sync_board(repo)
    return lines + [text for _, text in found]


def main():
    repo = repo_dir()
    due = network_due(state_file(repo, CHECK_FILE))
    lines = online(repo) if due else []
    lines += resync(repo) + [text for _, text in add_hooks(config_dir(), repo)]
    if checkout_dir(repo.parent).is_dir():
        lines.append(f"{LABEL} {force_mode(mode_file())}")
    if due:
        lines.append(start_background(repo, state_file(repo, GRAPHIFY_FILE)))
    for line in lines:
        if not QUIET.fullmatch(line):
            print(f"{PREFIX}: {line}")
    return DONE


if __name__ == "__main__":
    sys.exit(run_guarded(main, HINT))
