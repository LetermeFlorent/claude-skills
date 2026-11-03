import sys

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from gitcalls import (GitFailed, GitMissing, changed_paths, current_release, fast_forward, fetch_tag, head,
                      is_ancestor, is_dirty, latest_release)
from graphify import start_background
from guard import run_guarded
from hook import add_hooks
from paths import GRAPHIFY_FILE, INSTALLED_FILE, PONYTAIL_FILE, config_dir, repo_dir, skill_names, state_file
from ponytail import sync_ponytail
from registry import read_json, write_json
from sync import UNCHANGED, sync

PREFIX = "claude-skills"
DONE = 0
HINT = 'by hand: git -C "<config>/claude-skills" pull --ff-only, then run tools/install.py, see INSTALL.md'


def resync(repo):
    registry_path = state_file(repo, INSTALLED_FILE)
    registry, lines = sync(repo, repo.parent, read_json(registry_path))
    write_json(registry_path, registry)
    return [text for _, text in lines if not text.endswith(UNCHANGED)]


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
    fast_forward(repo, f"{tag}^{{commit}}")
    names = changed_skills(repo, old, head(repo), before)
    return [f"updated {was} to {tag}: {', '.join(names) or 'tools only'}", *resync(repo)]


def extras(repo):
    found = sync_ponytail(repo.parent, state_file(repo, PONYTAIL_FILE)) + add_hooks(config_dir(), repo)
    lines = [text for _, text in found if not text.endswith(UNCHANGED)]
    return lines + [start_background(repo, state_file(repo, GRAPHIFY_FILE))]


def main():
    repo = repo_dir()
    try:
        lines = check(repo)
    except GitMissing:
        lines = ["git not found: update skipped"]
    lines += extras(repo)
    for line in lines:
        print(f"{PREFIX}: {line}")
    return DONE


if __name__ == "__main__":
    sys.exit(run_guarded(main, HINT))
