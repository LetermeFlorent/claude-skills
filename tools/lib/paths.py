import os
from pathlib import Path

CONFIG_VAR = "CLAUDE_CONFIG_DIR"
DEFAULT_CONFIG = ".claude"
REPO_NAME = "claude-skills"
STATE_DIR = ".ia"
INSTALLED_FILE = "installed.json"
UPDATE_FILE = "update.json"
SKILL_FILE = "SKILL.md"
SKILLS_DIR = "skills"
COMMANDS_DIR = "commands"
COMMAND_GLOB = "*.md"


def config_dir(environ=None, home=None):
    environ = os.environ if environ is None else environ
    value = environ.get(CONFIG_VAR, "").strip()
    if value:
        return Path(value).expanduser()
    return Path(home or Path.home()) / DEFAULT_CONFIG


def repo_dir():
    return Path(__file__).resolve().parents[2]


def state_file(repo, name):
    return Path(repo) / STATE_DIR / name


def skill_names(repo):
    return sorted(entry.name for entry in Path(repo).iterdir()
                  if entry.is_dir() and (entry / SKILL_FILE).is_file())


def command_files(repo):
    found = {}
    for name in skill_names(repo):
        for path in sorted((Path(repo) / name / COMMANDS_DIR).glob(COMMAND_GLOB)):
            found[path.name] = path
    return found
