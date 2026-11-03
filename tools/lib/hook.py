import json
import sys
from collections import namedtuple
from pathlib import Path

SETTINGS = "settings.json"
ENCODING = "utf-8"
Hook = namedtuple("Hook", "label event matcher script argument timeout")
HOOKS = (Hook("update hook", "SessionStart", "startup", "tools/update.py", "", 30),
         Hook("resource hook", "PreToolUse", "Bash", "resource-guard/scripts/guard.py", " hook", 330))


def hook_command(repo, hook):
    python = Path(sys.executable).as_posix()
    script = (Path(repo) / hook.script).as_posix()
    return f'"{python}" -I "{script}"{hook.argument}'


def is_ours(entry, hook):
    mark = f"claude-skills/{hook.script}"
    return any(mark in str(item.get("command", "")) for item in entry.get("hooks", []) if isinstance(item, dict))


def read_settings(path):
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding=ENCODING))
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not hold a JSON object")
    return data


def write_settings(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding=ENCODING)


def _others(entries, hook):
    return [entry for entry in entries if not (isinstance(entry, dict) and is_ours(entry, hook))]


def _add(data, repo, hook):
    entries = data.setdefault("hooks", {}).setdefault(hook.event, [])
    command = {"type": "command", "command": hook_command(repo, hook), "timeout": hook.timeout}
    wanted = {"matcher": hook.matcher, "hooks": [command]}
    kept = _others(entries, hook)
    if kept + [wanted] == entries:
        return False, f"{hook.label}: already there"
    data["hooks"][hook.event] = kept + [wanted]
    return True, f"{hook.label}: added"


def _remove(data, hook):
    hooks = data.get("hooks", {})
    entries = hooks.get(hook.event, [])
    kept = _others(entries, hook)
    if kept == entries:
        return False, f"{hook.label}: none"
    if kept:
        hooks[hook.event] = kept
    else:
        hooks.pop(hook.event, None)
    if not hooks:
        data.pop("hooks", None)
    return True, f"{hook.label}: removed"


def _apply(config, change, failure):
    path = Path(config) / SETTINGS
    try:
        data = read_settings(path)
    except (ValueError, OSError) as error:
        return [(False, failure(hook, error)) for hook in HOOKS]
    results = [change(data, hook) for hook in HOOKS]
    if any(changed for changed, _ in results):
        write_settings(path, data)
    return [(True, text) for _, text in results]


def add_hooks(config, repo):
    def failure(hook, error):
        return f"{hook.label}: not added, {error}; add a {hook.event} hook running {hook_command(repo, hook)}"
    return _apply(config, lambda data, hook: _add(data, repo, hook), failure)


def remove_hooks(config):
    return _apply(config, _remove, lambda hook, error: f"{hook.label}: not removed, {error}")
