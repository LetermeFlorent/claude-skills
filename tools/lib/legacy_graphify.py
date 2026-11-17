import shutil
import subprocess
import sys

from paths import SKILLS_DIR

PACKAGE = "graphifyy"
NAME = "graphify"
MARK = ".claude-skills"
TIMEOUT = 600
LOW_PRIORITY = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)


def run(command):
    return subprocess.run(command, capture_output=True, text=True, errors="replace", timeout=TIMEOUT,
                          creationflags=LOW_PRIORITY)


def uninstall_command():
    uv = shutil.which("uv")
    if uv:
        listed = run([uv, "tool", "list"])
        if not listed.returncode and any(line.startswith(PACKAGE) for line in listed.stdout.splitlines()):
            return [uv, "tool", "uninstall", PACKAGE]
    pip = [sys.executable, "-m", "pip"]
    if not run([*pip, "show", PACKAGE]).returncode:
        return [*pip, "uninstall", "-y", PACKAGE]
    return None


def drop_package():
    try:
        command = uninstall_command()
        done = run(command) if command else None
    except (OSError, subprocess.SubprocessError) as error:
        return [(False, f"{NAME} package: not removed ({error})")]
    if done is None:
        return []
    if done.returncode:
        return [(False, f"{NAME} package: not removed ({(done.stderr or done.stdout).strip()})")]
    return [(True, f"{NAME} package: removed")]


def drop_skill_folder(config):
    folder = config / SKILLS_DIR / NAME
    if not (folder / MARK).is_file():
        return []
    try:
        shutil.rmtree(folder)
    except OSError as error:
        return [(False, f"{NAME} skill: not removed ({error})")]
    return [(True, f"{NAME} skill: removed")]


def drop_graphify(config):
    return drop_skill_folder(config) + drop_package()
