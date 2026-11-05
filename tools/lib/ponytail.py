import os
from pathlib import Path

from checkout import remove_checkout, update_checkout
from gitcalls import GitFailed, GitMissing
from opencode_ponytail import sync_opencode, unsync_opencode
from paths import SKILLS_DIR
from registry import read_json, write_json
from sync import drop_skill, sync_skills

URL = "https://github.com/DietrichGebert/ponytail"
URL_VAR = "CLAUDE_SKILLS_PONYTAIL_URL"
FOLDER = "ponytail"
MODE = "ultra"
MODE_KEY = "defaultMode"
LABEL = "ponytail"
SKILLS_KEY = "skills"


def checkout_dir(config):
    return Path(config) / FOLDER


def mode_file(environ=None, home=None):
    environ = os.environ if environ is None else environ
    home = Path(home or Path.home())
    if environ.get("XDG_CONFIG_HOME"):
        base = Path(environ["XDG_CONFIG_HOME"])
    elif os.name == "nt":
        base = Path(environ.get("APPDATA") or home / "AppData" / "Roaming")
    else:
        base = home / ".config"
    return base / FOLDER / "config.json"


def force_mode(path):
    data = read_json(path)
    if data.get(MODE_KEY) == MODE:
        return f"mode {MODE}: already there"
    data[MODE_KEY] = MODE
    write_json(path, data)
    return f"mode {MODE}: set"


def sync_ponytail(config, registry_path):
    folder = checkout_dir(config)
    try:
        ok, text = update_checkout(folder, os.environ.get(URL_VAR) or URL)
    except (GitFailed, GitMissing) as error:
        ok, text = False, f"not updated ({error})"
    lines = [(ok, f"{LABEL}: {text}")]
    if not (folder / SKILLS_DIR).is_dir():
        return lines
    registry = read_json(registry_path)
    known = registry.get(SKILLS_KEY, [])
    registry[SKILLS_KEY] = sync_skills(folder / SKILLS_DIR, Path(config), known, lines)
    lines.append((True, f"{LABEL} {force_mode(mode_file())}"))
    sync_opencode(folder, registry, lines)
    write_json(registry_path, registry)
    return lines


def unsync_ponytail(config, registry_path):
    folder, lines = checkout_dir(config), []
    registry = read_json(registry_path)
    for name in registry.get(SKILLS_KEY, []):
        drop_skill(name, Path(config) / SKILLS_DIR / name, folder / SKILLS_DIR / name, lines)
    unsync_opencode(registry, lines)
    if remove_checkout(folder):
        lines.append((True, f"{LABEL}: removed"))
    if Path(registry_path).is_file():
        Path(registry_path).unlink()
    return lines
