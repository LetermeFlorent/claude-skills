import json
import sys
from collections import namedtuple
from pathlib import Path

SETTINGS = "settings.json"
ENCODING = "utf-8"
Hook = namedtuple("Hook", "label event matcher script argument timeout")
SHORT_TIMEOUT = 15
START_EVENTS = "startup|resume|clear|compact"
INJECT = "claude-skills/tools/inject.py"
HOOKS = (Hook("update hook", "SessionStart", "startup", "claude-skills/tools/update.py", "", 30),
         Hook("resource hook", "PreToolUse", "Bash", "claude-skills/resource-guard/scripts/guard.py", " hook", 330),
         Hook("speech and code start hook", "SessionStart", START_EVENTS, INJECT, " SessionStart", SHORT_TIMEOUT),
         Hook("speech and code subagent hook", "SubagentStart", "", INJECT, " SubagentStart", SHORT_TIMEOUT))


def hook_command(repo, hook):
    script = (Path(repo).parent / hook.script).as_posix()
    return f'"{Path(sys.executable).as_posix()}" -I "{script}"{hook.argument}'


def is_ours(entry, hook):
    return any(hook.script in str(item.get("command", "")) for item in entry.get("hooks", []) if isinstance(item, dict))


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
    wanted = {"matcher": hook.matcher, "hooks": [command]} if hook.matcher else {"hooks": [command]}
    kept = _others(entries, hook)
    if len(entries) == len(kept) + 1 and wanted in entries:
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


def _apply(config, change, failure, hooks=HOOKS):
    path = Path(config) / SETTINGS
    try:
        data = read_settings(path)
    except (ValueError, OSError) as error:
        return [(False, failure(hook, error)) for hook in hooks]
    results = [change(data, hook) for hook in hooks]
    if any(changed for changed, _ in results):
        write_settings(path, data)
    return [(True, text) for _, text in results]


def add_hooks(config, repo):
    def failure(hook, error):
        return f"{hook.label}: not added, {error}; add a {hook.event} hook running {hook_command(repo, hook)}"
    return _apply(config, lambda data, hook: _add(data, repo, hook), failure)


def remove_hooks(config):
    return _apply(config, _remove, lambda hook, error: f"{hook.label}: not removed, {error}")
