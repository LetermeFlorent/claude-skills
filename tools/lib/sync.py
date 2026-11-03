import os
import shutil

from links import is_link, make_link, manual_command, points_at, remove_link, same_path
from paths import COMMANDS_DIR, SKILLS_DIR, command_files, opencode_dir, skill_names
from registry import file_hash

UNCHANGED = "already there"
AGAIN = "move it away and run install.py again"
SKILLS_KEY = "skills"
COMMANDS_KEY = "commands"
OPENCODE_KEY = "opencode_commands"
OPENCODE_LABEL = "opencode "


def sync(repo, config, registry):
    lines = []
    skills = sync_skills(repo, config, registry.get(SKILLS_KEY, []), lines)
    commands = sync_commands(repo, config / COMMANDS_DIR, registry.get(COMMANDS_KEY, {}), lines)
    result = {SKILLS_KEY: skills, COMMANDS_KEY: commands}
    other = opencode_dir()
    if other:
        known = registry.get(OPENCODE_KEY, {})
        result[OPENCODE_KEY] = sync_commands(repo, other / COMMANDS_DIR, known, lines, OPENCODE_LABEL)
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
    return {}, lines


def sync_skills(repo, config, known, lines):
    kept = []
    wanted = skill_names(repo)
    for name in wanted:
        link, target = config / SKILLS_DIR / name, repo / name
        if is_link(link) and same_path(link, target):
            kept.append(name)
            lines.append((True, f"skill {name}: {UNCHANGED}"))
        elif os.path.lexists(link):
            lines.append((False, f"skill {name}: skipped, {link} is not ours; {AGAIN}"))
        elif link_skill(name, link, target, lines):
            kept.append(name)
    for name in sorted(set(known) - set(wanted)):
        drop_skill(name, config / SKILLS_DIR / name, repo / name, lines)
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


def sync_commands(repo, folder, known, lines, label=""):
    kept = {}
    wanted = command_files(repo)
    for name, source in wanted.items():
        recorded = place_command(label + name, source, folder / name, known.get(name), lines)
        if recorded:
            kept[name] = recorded
    for name in sorted(set(known) - set(wanted)):
        drop_command(label + name, folder / name, known[name], lines)
    return kept


def place_command(name, source, dest, recorded, lines):
    current = file_hash(dest) if dest.is_file() else None
    wanted = file_hash(source)
    if current == wanted:
        lines.append((True, f"command {name}: {UNCHANGED}"))
        return wanted
    if current and not recorded:
        lines.append((False, f"command {name}: skipped, {dest} is not ours; {AGAIN}"))
        return None
    if current and current != recorded:
        lines.append((False, f"command {name}: changed by hand, left as is and no longer updated"))
        return None
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    except OSError as error:
        lines.append((False, f"command {name}: not copied ({error})"))
        return None
    lines.append((True, f"command {name}: copied"))
    return wanted


def drop_command(name, dest, recorded, lines):
    if not dest.is_file():
        return
    if file_hash(dest) != recorded:
        lines.append((False, f"command {name}: changed by hand, left as is"))
        return
    dest.unlink()
    lines.append((True, f"command {name}: removed"))
