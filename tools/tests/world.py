import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / "lib"))

from links import is_link, remove_link

ENCODING = "utf-8"
TIMEOUT = 120
SESSION_VAR = "CLAUDE_CODE_SESSION_ID"
CONFIG_VAR = "CLAUDE_CONFIG_DIR"
ROOT_PREFIX = "claude skills test "
GIT_OPTIONS = ("-c", "user.name=test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false",
               "-c", "core.autocrlf=false", "-c", "init.defaultBranch=main")
SKILL_TEXT = "---\nname: {0}\ndescription: Use when testing {0}.\n---\n\n# {0}\n"
COMMAND_TEXT = "Read the {0} skill.\n"
IGNORED = ".ia/\n__pycache__/\n"
BRANCH = "main"


def git(folder, *args):
    done = subprocess.run(["git", *GIT_OPTIONS, "-C", str(folder), *args], capture_output=True, text=True,
                          timeout=TIMEOUT)
    if done.returncode != 0:
        raise AssertionError(f"git {args[0]}: {done.stderr}")
    return done.stdout.strip()


def _force(function, path, _):
    os.chmod(path, stat.S_IWRITE)
    function(path)


class World:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix=ROOT_PREFIX))
        self.source = self.root / "source"
        self.origin = self.root / "origin.git"
        self.config = self.root / "config"
        self.clone = self.config / "claude-skills"
        shutil.copytree(TOOLS, self.source / "tools", ignore=shutil.ignore_patterns("tests", "__pycache__"))
        (self.source / ".gitignore").write_text(IGNORED, encoding=ENCODING)
        git(self.source, "init", "-q")
        self.write_skill("alpha")
        self.commit("start", "tools", ".gitignore", "alpha")
        git(self.root, "clone", "-q", "--bare", str(self.source), str(self.origin))
        git(self.source, "remote", "add", "origin", str(self.origin))
        git(self.root, "clone", "-q", str(self.origin), str(self.clone))

    def write_skill(self, name, command=None):
        folder = self.source / name / "commands"
        folder.mkdir(parents=True, exist_ok=True)
        (folder.parent / "SKILL.md").write_text(SKILL_TEXT.format(name), encoding=ENCODING)
        (folder / f"{name}.md").write_text(command or COMMAND_TEXT.format(name), encoding=ENCODING)

    def commit(self, message, *paths):
        git(self.source, "add", "--", *paths)
        git(self.source, "commit", "-q", "-m", message)

    def publish(self, message, *paths):
        self.commit(message, *paths)
        git(self.source, "push", "-q", "origin", BRANCH)

    def publish_removal(self, name):
        git(self.source, "rm", "-r", "-q", name)
        git(self.source, "commit", "-q", "-m", f"remove {name}")
        git(self.source, "push", "-q", "origin", BRANCH)

    def run(self, script, *args, session=None, path=None, tools=None):
        env = {key: value for key, value in os.environ.items() if key != SESSION_VAR}
        env[CONFIG_VAR] = str(self.config)
        if session:
            env[SESSION_VAR] = session
        if path is not None:
            env["PATH"] = str(path)
        folder = tools or self.clone / "tools"
        return subprocess.run([sys.executable, "-I", str(folder / script), *args], capture_output=True,
                              text=True, cwd=self.root, env=env, timeout=TIMEOUT)

    def skill_link(self, name):
        return self.config / "skills" / name

    def command(self, name):
        return self.config / "commands" / name

    def close(self):
        skills = self.config / "skills"
        for entry in skills.iterdir() if skills.is_dir() else []:
            if is_link(entry):
                remove_link(entry)
        handler = {"onexc": _force} if sys.version_info >= (3, 12) else {"onerror": _force}
        shutil.rmtree(self.root, **handler)
