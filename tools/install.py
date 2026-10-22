import sys

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from guard import run_guarded
from links import same_path
from paths import INSTALLED_FILE, REPO_NAME, config_dir, repo_dir, state_file
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
    registry, lines = unsync(config, registry) if argv else sync(repo, config, registry)
    write_json(registry_path, registry)
    for _, text in lines:
        print(text)
    return DONE if all(ok for ok, _ in lines) else FAILED


if __name__ == "__main__":
    sys.exit(run_guarded(lambda: main(sys.argv[1:]), HINT))
