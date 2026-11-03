import os
import shutil
import stat
import sys
from pathlib import Path

from gitcalls import GitFailed, GitMissing, git, latest_release
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


def installed_tag(folder):
    try:
        return git(folder, "describe", "--tags", "--exact-match", "HEAD")
    except GitFailed:
        return ""


def update_checkout(folder):
    if folder.exists() and not (folder / ".git").is_dir():
        return False, f"{folder} is not ours, left as is"
    if not folder.exists():
        folder.mkdir(parents=True)
        git(folder, "init", "--quiet")
        git(folder, "remote", "add", "origin", os.environ.get(URL_VAR) or URL)
    latest = latest_release(folder)
    if latest is None:
        return False, "no release found"
    tag, was = latest[0], installed_tag(folder)
    if was == tag:
        return True, f"up to date ({tag})"
    git(folder, "fetch", "--quiet", "--depth", "1", "--no-tags", "origin", f"refs/tags/{tag}:refs/tags/{tag}")
    git(folder, "checkout", "--quiet", "--force", "--detach", f"{tag}^{{commit}}")
    return True, f"updated {was} to {tag}" if was else f"installed {tag}"


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
        ok, text = update_checkout(folder)
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


def _force(function, path, _):
    os.chmod(path, stat.S_IWRITE)
    function(path)


def unsync_ponytail(config, registry_path):
    folder, lines = checkout_dir(config), []
    registry = read_json(registry_path)
    for name in registry.get(SKILLS_KEY, []):
        drop_skill(name, Path(config) / SKILLS_DIR / name, folder / SKILLS_DIR / name, lines)
    unsync_opencode(registry, lines)
    if (folder / ".git").is_dir():
        handler = {"onexc": _force} if sys.version_info >= (3, 12) else {"onerror": _force}
        shutil.rmtree(folder, **handler)
        lines.append((True, f"{LABEL}: removed"))
    if Path(registry_path).is_file():
        Path(registry_path).unlink()
    return lines
