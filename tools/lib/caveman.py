import os
from pathlib import Path

from checkout import remove_checkout, update_checkout
from gitcalls import GitFailed, GitMissing
from paths import SKILLS_DIR
from registry import read_json, write_json
from sync import drop_command, drop_skill, place_command, sync_skills

URL = "https://github.com/JuliusBrussee/caveman"
URL_VAR = "CLAUDE_SKILLS_CAVEMAN_URL"
FOLDER = "caveman"
LABEL = "caveman"
SKILLS = ("cavecrew", "caveman-explore")
AGENTS_DIR = "agents"
AGENT_GLOB = "cavecrew-*.md"
AGENT_KIND = "caveman agent"
SKILLS_KEY = "skills"
AGENTS_KEY = "agents"


def checkout_dir(config):
    return Path(config) / FOLDER


def sync_agents(folder, config, known, lines):
    kept = {}
    wanted = {path.name: path for path in sorted((folder / AGENTS_DIR).glob(AGENT_GLOB))}
    for name, source in wanted.items():
        recorded = place_command(name, source, config / AGENTS_DIR / name, known.get(name), lines, AGENT_KIND)
        if recorded:
            kept[name] = recorded
    for name in sorted(set(known) - set(wanted)):
        drop_command(name, config / AGENTS_DIR / name, known[name], lines, AGENT_KIND)
    return kept


def sync_caveman(config, registry_path):
    folder, config = checkout_dir(config), Path(config)
    try:
        ok, text = update_checkout(folder, os.environ.get(URL_VAR) or URL)
    except (GitFailed, GitMissing) as error:
        ok, text = False, f"not updated ({error})"
    lines = [(ok, f"{LABEL}: {text}")]
    if not (folder / SKILLS_DIR).is_dir():
        return lines
    registry = read_json(registry_path)
    wanted = [name for name in SKILLS if (folder / SKILLS_DIR / name).is_dir()]
    registry[SKILLS_KEY] = sync_skills(folder / SKILLS_DIR, config, registry.get(SKILLS_KEY, []), lines, wanted)
    registry[AGENTS_KEY] = sync_agents(folder, config, registry.get(AGENTS_KEY, {}), lines)
    write_json(registry_path, registry)
    return lines


def unsync_caveman(config, registry_path):
    folder, config, lines = checkout_dir(config), Path(config), []
    registry = read_json(registry_path)
    for name in registry.get(SKILLS_KEY, []):
        drop_skill(name, config / SKILLS_DIR / name, folder / SKILLS_DIR / name, lines)
    for name, recorded in registry.get(AGENTS_KEY, {}).items():
        drop_command(name, config / AGENTS_DIR / name, recorded, lines, AGENT_KIND)
    if remove_checkout(folder):
        lines.append((True, f"{LABEL}: removed"))
    if Path(registry_path).is_file():
        Path(registry_path).unlink()
    return lines
