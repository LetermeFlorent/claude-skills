import json
import shutil
import subprocess
from pathlib import Path

from paths import COMMANDS_DIR, COMMAND_GLOB, opencode_dir
from sync import OPENCODE_LABEL, drop_command, place_command

COMMANDS_KEY = "opencode_commands"
RULES_KEY = "opencode_rules"
RULES_FILE = "ponytail-ultra.md"
SOURCE_COMMANDS = (".opencode", "command")
BUILDER = ("hooks", "ponytail-instructions.js")
CONFIG_NAMES = ("opencode.jsonc", "opencode.json")
INSTRUCTIONS = "instructions"
ENCODING = "utf-8"
TIMEOUT = 20
LABEL = "ponytail opencode rules"


def config_file(folder):
    found = [folder / name for name in CONFIG_NAMES if (folder / name).is_file()]
    return found[0] if found else folder / CONFIG_NAMES[-1]


def ultra_rules(checkout):
    node = shutil.which("node")
    if node is None:
        return None
    script = (checkout.joinpath(*BUILDER)).as_posix()
    code = f"process.stdout.write(require({json.dumps(script)}).getPonytailInstructions('ultra'))"
    done = subprocess.run([node, "-e", code], capture_output=True, encoding=ENCODING, errors="replace",
                          timeout=TIMEOUT)
    return done.stdout if done.returncode == 0 and done.stdout.strip() else None


def edit_instructions(folder, rules, keep):
    path = config_file(folder)
    data = json.loads(path.read_text(encoding=ENCODING)) if path.is_file() else {}
    entries = [entry for entry in data.get(INSTRUCTIONS, []) if entry != rules.as_posix()]
    entries += [rules.as_posix()] if keep else []
    if entries == data.get(INSTRUCTIONS, []):
        return False
    if entries:
        data[INSTRUCTIONS] = entries
    else:
        data.pop(INSTRUCTIONS, None)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding=ENCODING)
    return True


def sync_rules(checkout, folder, registry, lines):
    rules, text = folder / RULES_FILE, ultra_rules(checkout)
    if text is None:
        lines.append((False, f"{LABEL}: not written, node not found or failed"))
        return
    changed = not rules.is_file() or rules.read_text(encoding=ENCODING) != text
    if changed:
        rules.write_text(text, encoding=ENCODING)
    registry[RULES_KEY] = rules.as_posix()
    try:
        changed = edit_instructions(folder, rules, True) or changed
    except ValueError:
        lines.append((False, f"{LABEL}: add {rules.as_posix()} to {INSTRUCTIONS} in {config_file(folder)} by hand"))
        return
    lines.append((True, f"{LABEL}: {'written' if changed else 'already there'}"))


def sync_opencode(checkout, registry, lines):
    folder = opencode_dir()
    if folder is None:
        return
    known, kept = registry.get(COMMANDS_KEY, {}), {}
    for source in sorted(checkout.joinpath(*SOURCE_COMMANDS).glob(COMMAND_GLOB)):
        dest = folder / COMMANDS_DIR / source.name
        recorded = place_command(OPENCODE_LABEL + source.name, source, dest, known.get(source.name), lines)
        if recorded:
            kept[source.name] = recorded
    for name in sorted(set(known) - set(kept)):
        drop_command(OPENCODE_LABEL + name, folder / COMMANDS_DIR / name, known[name], lines)
    registry[COMMANDS_KEY] = kept
    sync_rules(checkout, folder, registry, lines)


def unsync_opencode(registry, lines):
    folder = opencode_dir()
    if folder is None:
        return
    for name, recorded in registry.get(COMMANDS_KEY, {}).items():
        drop_command(OPENCODE_LABEL + name, folder / COMMANDS_DIR / name, recorded, lines)
    rules = Path(registry.get(RULES_KEY, folder / RULES_FILE))
    try:
        edit_instructions(folder, rules, False)
    except ValueError:
        lines.append((False, f"{LABEL}: remove {rules.as_posix()} from {config_file(folder)} by hand"))
    if rules.is_file():
        rules.unlink()
        lines.append((True, f"{LABEL}: removed"))
