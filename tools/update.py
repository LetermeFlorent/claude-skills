import os
import sys
import time

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from gitcalls import (GitFailed, GitMissing, changed_paths, fast_forward, fetch, head, is_ancestor, is_dirty,
                      remote_head, top_folders)
from guard import run_guarded
from paths import INSTALLED_FILE, UPDATE_FILE, config_dir, repo_dir, skill_names, state_file
from registry import already_checked, read_json, stamp, write_json
from sync import UNCHANGED, sync

BRANCH = "main"
RECHECK_HOURS = 12
SESSION_VAR = "CLAUDE_CODE_SESSION_ID"
SHORT = 7
DONE = 0
REREAD = "Re-read the SKILL.md of the skill in use before going on."
HINT = 'by hand: git -C "<config>/claude-skills" pull --ff-only, then run tools/install.py, see INSTALL.md'


def current_head(repo):
    try:
        return head(repo)
    except (GitFailed, GitMissing):
        return ""


def resync(repo, config):
    registry_path = state_file(repo, INSTALLED_FILE)
    registry, lines = sync(repo, config, read_json(registry_path))
    write_json(registry_path, registry)
    for _, text in lines:
        if not text.endswith(UNCHANGED):
            print(text)


def check(repo, config):
    if is_dirty(repo):
        return "local changes: not updated"
    old = head(repo)
    try:
        new = remote_head(repo, BRANCH)
        if new != old:
            fetch(repo, BRANCH)
    except GitFailed:
        return f"could not reach GitHub: kept {old[:SHORT]}"
    if new == old:
        return f"up to date ({old[:SHORT]})"
    if not is_ancestor(repo, old):
        return "local commits: not updated"
    before = skill_names(repo)
    fast_forward(repo)
    resync(repo, config)
    names = top_folders(changed_paths(repo, old, new), before + skill_names(repo))
    return f"updated {old[:SHORT]}..{new[:SHORT]}: {', '.join(names) or 'tools only'}. {REREAD}"


def main():
    repo, config = repo_dir(), config_dir()
    session = os.environ.get(SESSION_VAR, "").strip()
    state_path = state_file(repo, UPDATE_FILE)
    if already_checked(read_json(state_path), session, time.time(), RECHECK_HOURS):
        print("already checked this session")
        return DONE
    try:
        print(check(repo, config))
    except GitMissing:
        print("git not found: update skipped")
    finally:
        write_json(state_path, stamp(session, time.time(), current_head(repo)))
    return DONE


if __name__ == "__main__":
    sys.exit(run_guarded(main, HINT))
