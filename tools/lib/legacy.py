import os
from pathlib import Path
from types import SimpleNamespace

from hook import SETTINGS, is_ours as marked, read_settings, write_settings
from legacy_graphify import drop_graphify
from legacy_opencode import drop_opencode
from legacy_ops import drop_checkout, drop_file, drop_link, succeeded
from paths import SKILLS_DIR, state_file
from registry import read_json, write_json

PONYTAIL = "ponytail"
CAVEMAN = "caveman"
GRAPHIFY = "graphify"
AGENTS_DIR = "agents"
MODE_KEY = "defaultMode"
MODE = "ultra"
HOOK_MARK = SimpleNamespace(script="ponytail/hooks/")
LEFT_OVER = (".log", ".lock")


def mode_file(environ=None, home=None):
    environ = os.environ if environ is None else environ
    home = Path(home or Path.home())
    if environ.get("XDG_CONFIG_HOME"):
        base = Path(environ["XDG_CONFIG_HOME"])
    elif os.name == "nt":
        base = Path(environ.get("APPDATA") or home / "AppData" / "Roaming")
    else:
        base = home / ".config"
    return base / PONYTAIL / "config.json"


def drop_mode(path):
    data = read_json(path)
    if data.get(MODE_KEY) != MODE:
        return []
    data.pop(MODE_KEY)
    try:
        if data:
            write_json(path, data)
        else:
            path.unlink()
            if not any(path.parent.iterdir()):
                path.parent.rmdir()
    except OSError as error:
        return [(False, f"{PONYTAIL} mode: not removed ({error})")]
    return [(True, f"{PONYTAIL} mode: removed")]


def drop_skills(label, config, registry):
    lines = []
    for name in registry.get("skills", []):
        lines += drop_link(f"{label} skill {name}", config / SKILLS_DIR / name, config / label / SKILLS_DIR / name)
    return lines


def ponytail(config, registry):
    lines = drop_skills(PONYTAIL, config, registry) + drop_opencode(registry) + drop_mode(mode_file())
    return lines + (drop_checkout(PONYTAIL, config / PONYTAIL) if succeeded(lines) else [])


def caveman(config, registry):
    lines = drop_skills(CAVEMAN, config, registry)
    for name, recorded in registry.get("agents", {}).items():
        lines += drop_file(f"{CAVEMAN} agent {name}", config / AGENTS_DIR / name, recorded)
    return lines + (drop_checkout(CAVEMAN, config / CAVEMAN) if succeeded(lines) else [])


def part(repo, config, name, work):
    state = state_file(repo, f"{name}.json")
    if not state.is_file():
        return []
    lines = work(config, read_json(state))
    if succeeded(lines):
        state.unlink()
        for suffix in LEFT_OVER:
            state.with_suffix(suffix).unlink(missing_ok=True)
    return lines


def drop_hooks(config):
    path = config / SETTINGS
    try:
        data = read_settings(path)
    except (ValueError, OSError):
        return []
    hooks, lines = data.get("hooks"), []
    for event, entries in list(hooks.items() if isinstance(hooks, dict) else ()):
        if not isinstance(entries, list):
            continue
        kept = [entry for entry in entries if not (isinstance(entry, dict) and marked(entry, HOOK_MARK))]
        lines += [(True, f"{PONYTAIL} hook {event}: removed")] * (len(entries) - len(kept))
        hooks[event] = kept
        if not kept:
            hooks.pop(event)
    if not lines:
        return []
    if not hooks:
        data.pop("hooks")
    try:
        write_settings(path, data)
    except OSError as error:
        return [(False, f"{PONYTAIL} hooks: not removed ({error})")]
    return lines


def clean(repo, config):
    config = Path(config)
    lines = part(repo, config, PONYTAIL, ponytail)
    lines += part(repo, config, CAVEMAN, caveman)
    lines += part(repo, config, GRAPHIFY, lambda folder, _: drop_graphify(folder))
    return lines + drop_hooks(config)
