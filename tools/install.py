import sys

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from board import sync_board, unsync_board
from caveman import sync_caveman, unsync_caveman
from graphify import sync_graphify, uninstall
from guard import run_guarded
from hook import add_hooks, remove_hooks
from links import same_path
from paths import CAVEMAN_FILE, GRAPHIFY_FILE, INSTALLED_FILE, PONYTAIL_FILE, REPO_NAME, config_dir, repo_dir, state_file
from ponytail import sync_ponytail, unsync_ponytail
from registry import read_json, write_json
from sync import sync, unsync

TOOL = "install"
UNINSTALL = "--uninstall"
DONE, FAILED, REFUSED = 0, 1, 2
HINT = 'by hand: python -I "<config>/claude-skills/tools/install.py", see INSTALL.md'


def main(argv):
    if argv not in ([], [UNINSTALL]):
        print(f"{TOOL}: no argument to install, {UNINSTALL} to remove")
        return REFUSED
    repo, config = repo_dir(), config_dir()
    if not same_path(repo, config / REPO_NAME):
        print(f"{TOOL}: the repository is in {repo}, clone it into {config / REPO_NAME}")
        return REFUSED
    registry_path = state_file(repo, INSTALLED_FILE)
    registry = read_json(registry_path)
    registry, lines = unsync(repo, config, registry) if argv else sync(repo, config, registry)
    write_json(registry_path, registry)
    ponytail_state = state_file(repo, PONYTAIL_FILE)
    lines.extend(unsync_ponytail(config, ponytail_state) if argv else sync_ponytail(config, ponytail_state))
    caveman_state = state_file(repo, CAVEMAN_FILE)
    lines.extend(unsync_caveman(config, caveman_state) if argv else sync_caveman(config, caveman_state))
    graphify_state = state_file(repo, GRAPHIFY_FILE)
    lines.extend(uninstall(config, graphify_state) if argv else sync_graphify(config, graphify_state))
    lines.extend(remove_hooks(config) if argv else add_hooks(config, repo))
    lines.extend(unsync_board(repo) if argv else sync_board(repo))
    for _, text in lines:
        print(text)
    return DONE if all(ok for ok, _ in lines) else FAILED


if __name__ == "__main__":
    sys.exit(run_guarded(lambda: main(sys.argv[1:]), HINT))
