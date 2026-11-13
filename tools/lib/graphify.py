import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from paths import SKILLS_DIR
from registry import read_json, write_json

PACKAGE = "graphifyy"
INDEX = "https://pypi.org/pypi/graphifyy/json"
INDEX_VAR = "CLAUDE_SKILLS_GRAPHIFY_INDEX"
NAME = "graphify"
MARK = ".claude-skills"
VERSION_KEY = "version"
LOCK_SECONDS = 900
TIMEOUT = 10
INSTALL_TIMEOUT = 600
DETACHED = sum(getattr(subprocess, flag, 0) for flag in
               ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "BELOW_NORMAL_PRIORITY_CLASS"))
DESCRIPTION = ("description: \"Use only in a large codebase (about 300 or more tracked source files, 50,000 or more "
               "lines, or a monorepo), when a graphify-out/ folder already exists, or when the user types /graphify: "
               "build or query a knowledge graph of the code before reading files one by one. Skip it on a small "
               "project.\"")


def latest_version():
    with urllib.request.urlopen(os.environ.get(INDEX_VAR) or INDEX, timeout=TIMEOUT) as answer:
        return json.load(answer)["info"]["version"]


def skill_dir(config):
    return Path(config) / SKILLS_DIR / NAME


def is_ours(folder):
    return not folder.exists() or (folder / MARK).is_file()


def narrow(text):
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith("description:"):
            lines[index] = DESCRIPTION + "\n"
            return "".join(lines)
    return text


def runner():
    found = shutil.which(NAME)
    return [found] if found else [sys.executable, "-m", NAME]


def install_command():
    uv = shutil.which("uv")
    if uv:
        return [uv, "tool", "install", "--upgrade", PACKAGE]
    return [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "--quiet", "--disable-pip-version-check",
            PACKAGE]


def place_skill(staged, dest):
    if not (staged / "SKILL.md").is_file():
        raise FileNotFoundError(f"graphify's installer wrote no {staged / 'SKILL.md'}")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(staged, dest)
    skill = dest / "SKILL.md"
    skill.write_text(narrow(skill.read_text(encoding="utf-8")), encoding="utf-8")
    (dest / MARK).write_text("", encoding="utf-8")


def stage_and_place(dest):
    with tempfile.TemporaryDirectory(prefix="graphify-home-") as home:
        env = {**os.environ, "HOME": home, "USERPROFILE": home}
        env.pop("CLAUDE_CONFIG_DIR", None)
        platform = "windows" if os.name == "nt" else "claude"
        subprocess.run([*runner(), "install", "--platform", platform], env=env, capture_output=True,
                       timeout=INSTALL_TIMEOUT, check=True)
        place_skill(Path(home) / ".claude" / SKILLS_DIR / NAME, dest)


def install_now(config, state_path, version):
    dest = skill_dir(config)
    if not is_ours(dest):
        return False, f"{NAME}: {dest} is not ours, left as is"
    try:
        subprocess.run(install_command(), capture_output=True, timeout=INSTALL_TIMEOUT, check=True)
        stage_and_place(dest)
    except (OSError, subprocess.SubprocessError) as error:
        return False, f"{NAME}: not installed ({error})"
    write_json(state_path, {VERSION_KEY: version})
    return True, f"{NAME}: installed {version}"


def needed(config, state_path):
    try:
        latest = latest_version()
    except (OSError, ValueError, KeyError) as error:
        return None, f"{NAME}: could not reach PyPI ({error}), kept as is"
    current = read_json(state_path).get(VERSION_KEY)
    if current == latest and (skill_dir(config) / "SKILL.md").is_file():
        return None, f"{NAME}: up to date ({latest})"
    return latest, ""


def fresh_lock(lock):
    return lock.is_file() and time.time() - lock.stat().st_mtime < LOCK_SECONDS


def uninstall(config, state_path):
    dest, lines = skill_dir(config), []
    if dest.exists() and is_ours(dest):
        shutil.rmtree(dest)
        lines.append((True, f"{NAME}: skill removed, the {PACKAGE} package stays (pip uninstall {PACKAGE})"))
    if Path(state_path).is_file():
        Path(state_path).unlink()
    return lines


def sync_graphify(config, state_path):
    latest, text = needed(config, state_path)
    if latest is None:
        return [(True, text)]
    return [install_now(config, state_path, latest)]


def start_background(repo, state_path):
    latest, text = needed(repo.parent, state_path)
    lock = Path(state_path).with_suffix(".lock")
    if latest is None or fresh_lock(lock):
        return text or f"{NAME}: an install is already running"
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(latest, encoding="utf-8")
    script = Path(repo) / "tools" / "graphify_run.py"
    with open(Path(state_path).with_suffix(".log"), "a", encoding="utf-8") as log:
        subprocess.Popen([sys.executable, "-I", str(script), latest], stdout=log, stderr=log,
                         stdin=subprocess.DEVNULL, creationflags=DETACHED, start_new_session=os.name != "nt")
    return f"{NAME}: installing {latest} in the background"
