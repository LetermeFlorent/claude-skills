import os
import shutil

from links import is_link, make_link, manual_command, points_at, remove_link, same_path
from paths import COMMANDS_DIR, SKILLS_DIR, command_files, opencode_dir, qwen_dir, skill_names
from registry import file_hash, text_hash

ENCODING = "utf-8"
UNCHANGED = "already there"
AGAIN = "move it away and run install.py again"
SKILLS_KEY = "skills"
COMMANDS_KEY = "commands"
OPENCODE_KEY = "opencode_commands"
OPENCODE_LABEL = "opencode "
QWEN_SKILLS_KEY = "qwen_skills"
QWEN_COMMANDS_KEY = "qwen_commands"
QWEN_LABEL = "qwen "
CLAUDE_ARGUMENTS, QWEN_ARGUMENTS = "$ARGUMENTS", "{{args}}"
CLAUDE_ONLY_KEYS = ("allowed-tools:",)


def sync(repo, config, registry):
    lines = []
    skills = sync_skills(repo, config, registry.get(SKILLS_KEY, []), lines)
    commands = sync_commands(repo, config / COMMANDS_DIR, registry.get(COMMANDS_KEY, {}), lines)
    result = {SKILLS_KEY: skills, COMMANDS_KEY: commands}
    other = opencode_dir()
    if other:
        known = registry.get(OPENCODE_KEY, {})
        result[OPENCODE_KEY] = sync_commands(repo, other / COMMANDS_DIR, known, lines, OPENCODE_LABEL)
    qwen = qwen_dir()
    if qwen:
        result[QWEN_SKILLS_KEY] = sync_skills(repo, qwen, registry.get(QWEN_SKILLS_KEY, []), lines, QWEN_LABEL)
        known = registry.get(QWEN_COMMANDS_KEY, {})
        result[QWEN_COMMANDS_KEY] = sync_commands(repo, qwen / COMMANDS_DIR, known, lines, QWEN_LABEL, for_qwen)
    return result, lines


def unsync(repo, config, registry):
    lines = []
    for name in registry.get(SKILLS_KEY, []):
        drop_skill(name, config / SKILLS_DIR / name, repo / name, lines)
    for name, recorded in registry.get(COMMANDS_KEY, {}).items():
        drop_command(name, config / COMMANDS_DIR / name, recorded, lines)
    other = opencode_dir()
    for name, recorded in registry.get(OPENCODE_KEY, {}).items() if other else ():
        drop_command(OPENCODE_LABEL + name, other / COMMANDS_DIR / name, recorded, lines)
    qwen = qwen_dir()
    for name in registry.get(QWEN_SKILLS_KEY, []) if qwen else ():
        drop_skill(QWEN_LABEL + name, qwen / SKILLS_DIR / name, repo / name, lines)
    for name, recorded in registry.get(QWEN_COMMANDS_KEY, {}).items() if qwen else ():
        drop_command(QWEN_LABEL + name, qwen / COMMANDS_DIR / name, recorded, lines)
    return {}, lines


def for_qwen(text):
    kept = [line for line in text.splitlines(keepends=True) if not line.startswith(CLAUDE_ONLY_KEYS)]
    return "".join(kept).replace(CLAUDE_ARGUMENTS, QWEN_ARGUMENTS)


def sync_skills(repo, config, known, lines, label=""):
    kept = []
    wanted = skill_names(repo)
    for name in wanted:
        link, target = config / SKILLS_DIR / name, repo / name
        if is_link(link) and same_path(link, target):
            kept.append(name)
            lines.append((True, f"skill {label}{name}: {UNCHANGED}"))
        elif os.path.lexists(link):
            lines.append((False, f"skill {label}{name}: skipped, {link} is not ours; {AGAIN}"))
        elif link_skill(label + name, link, target, lines):
            kept.append(name)
    for name in sorted(set(known) - set(wanted)):
        drop_skill(label + name, config / SKILLS_DIR / name, repo / name, lines)
    return kept


def link_skill(name, link, target, lines):
    try:
        make_link(link, target)
    except OSError as error:
        lines.append((False, f"skill {name}: not linked ({error}); by hand: {manual_command(link, target)}"))
        return False
    lines.append((True, f"skill {name}: linked"))
    return True


def drop_skill(name, link, target, lines):
    if not os.path.lexists(link):
        return
    if not is_link(link):
        lines.append((False, f"skill {name}: {link} is not a link, left as is"))
        return
    if not points_at(link, target):
        lines.append((False, f"skill {name}: {link} points elsewhere, left as is"))
        return
    remove_link(link)
    lines.append((True, f"skill {name}: removed"))


def sync_commands(repo, folder, known, lines, label="", convert=None):
    kept = {}
    wanted = command_files(repo)
    for name, source in wanted.items():
        recorded = place_command(label + name, source, folder / name, known.get(name), lines, convert=convert)
        if recorded:
            kept[name] = recorded
    for name in sorted(set(known) - set(wanted)):
        drop_command(label + name, folder / name, known[name], lines)
    return kept


def place_command(name, source, dest, recorded, lines, kind="command", convert=None):
    current = file_hash(dest) if dest.is_file() else None
    text = convert(source.read_text(encoding=ENCODING)) if convert else None
    wanted = text_hash(text) if convert else file_hash(source)
    if current == wanted:
        lines.append((True, f"{kind} {name}: {UNCHANGED}"))
        return wanted
    if current and not recorded:
        lines.append((False, f"{kind} {name}: skipped, {dest} is not ours; {AGAIN}"))
        return None
    if current and current != recorded:
        lines.append((False, f"{kind} {name}: changed by hand, left as is and no longer updated"))
        return None
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if convert:
            dest.write_bytes(text.encode(ENCODING))
        else:
            shutil.copyfile(source, dest)
    except OSError as error:
        lines.append((False, f"{kind} {name}: not copied ({error})"))
        return recorded
    lines.append((True, f"{kind} {name}: copied"))
    return wanted


def drop_command(name, dest, recorded, lines, kind="command"):
    if not dest.is_file():
        return
    if file_hash(dest) != recorded:
        lines.append((False, f"{kind} {name}: changed by hand, left as is"))
        return
    try:
        dest.unlink()
    except OSError as error:
        lines.append((False, f"{kind} {name}: not removed ({error})"))
        return
    lines.append((True, f"{kind} {name}: removed"))
