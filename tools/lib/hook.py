import json
import shutil
import sys
from collections import namedtuple
from pathlib import Path

SETTINGS = "settings.json"
ENCODING = "utf-8"
NODE = "node"
Hook = namedtuple("Hook", "label event matcher script argument timeout")
PONYTAIL_START = "startup|resume|clear|compact"
HOOKS = (Hook("update hook", "SessionStart", "startup", "claude-skills/tools/update.py", "", 30),
         Hook("resource hook", "PreToolUse", "Bash", "claude-skills/resource-guard/scripts/guard.py", " hook", 330),
         Hook("ponytail start hook", "SessionStart", PONYTAIL_START, "ponytail/hooks/ponytail-activate.js", "", 15),
         Hook("ponytail subagent hook", "SubagentStart", "", "ponytail/hooks/ponytail-subagent.js", "", 15),
         Hook("ponytail mode hook", "UserPromptSubmit", "", "ponytail/hooks/ponytail-mode-tracker.js", "", 15))


def hook_command(repo, hook):
    script = (Path(repo).parent / hook.script).as_posix()
    if script.endswith(".js"):
        node = Path(shutil.which(NODE) or NODE).as_posix()
        return f'"{node}" "{script}"{hook.argument}'
    return f'"{Path(sys.executable).as_posix()}" -I "{script}"{hook.argument}'


def is_ours(entry, hook):
    return any(hook.script in str(item.get("command", "")) for item in entry.get("hooks", []) if isinstance(item, dict))


def ready(repo, hook):
    return not hook.script.endswith(".js") or (Path(repo).parent / hook.script).is_file()


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
    hooks = [hook for hook in HOOKS if ready(repo, hook)]
    return _apply(config, lambda data, hook: _add(data, repo, hook), failure, hooks)


def remove_hooks(config):
    return _apply(config, _remove, lambda hook, error: f"{hook.label}: not removed, {error}")
