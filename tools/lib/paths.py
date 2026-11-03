import os
from pathlib import Path

CONFIG_VAR = "CLAUDE_CONFIG_DIR"
OPENCODE_VAR = "CLAUDE_SKILLS_OPENCODE_DIR"
OPENCODE_DEFAULT = (".config", "opencode")
DEFAULT_CONFIG = ".claude"
REPO_NAME = "claude-skills"
STATE_DIR = ".ia"
INSTALLED_FILE = "installed.json"
PONYTAIL_FILE = "ponytail.json"
GRAPHIFY_FILE = "graphify.json"
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


def opencode_dir(environ=None, home=None):
    environ = os.environ if environ is None else environ
    if OPENCODE_VAR in environ:
        value = environ[OPENCODE_VAR].strip()
        return Path(value).expanduser() if value else None
    folder = Path(home or Path.home()).joinpath(*OPENCODE_DEFAULT)
    return folder if folder.is_dir() else None


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
