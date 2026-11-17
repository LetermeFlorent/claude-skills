import json
from pathlib import Path

from legacy_ops import drop_file
from paths import COMMANDS_DIR, opencode_dir

COMMANDS_KEY = "opencode_commands"
RULES_KEY = "opencode_rules"
CONFIG_NAMES = ("opencode.jsonc", "opencode.json")
INSTRUCTIONS = "instructions"
ENCODING = "utf-8"
LABEL = "ponytail opencode"


def config_file(folder):
    found = [folder / name for name in CONFIG_NAMES if (folder / name).is_file()]
    return found[0] if found else None


def drop_entry(path, rules):
    data = json.loads(path.read_text(encoding=ENCODING))
    if not isinstance(data, dict):
        raise ValueError("not a JSON object")
    entries = data.get(INSTRUCTIONS, [])
    kept = [entry for entry in entries if entry != rules.as_posix()]
    if kept == entries:
        return
    if kept:
        data[INSTRUCTIONS] = kept
    else:
        data.pop(INSTRUCTIONS, None)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding=ENCODING)


def drop_rules(folder, rules):
    path = config_file(folder)
    try:
        if path is not None:
            drop_entry(path, rules)
    except (ValueError, OSError):
        return [(True, f"{LABEL} rules: remove {rules.as_posix()} from {path} by hand")]
    if not rules.is_file():
        return []
    try:
        rules.unlink()
    except OSError as error:
        return [(False, f"{LABEL} rules: not removed ({error})")]
    return [(True, f"{LABEL} rules: removed")]


def drop_opencode(registry):
    folder, lines = opencode_dir(), []
    if folder is None:
        return lines
    for name, recorded in registry.get(COMMANDS_KEY, {}).items():
        lines += drop_file(f"{LABEL} command {name}", folder / COMMANDS_DIR / name, recorded)
    if registry.get(RULES_KEY):
        lines += drop_rules(folder, Path(registry[RULES_KEY]))
    return lines
