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
PONYTAIL_FILES = {"skills/ponytail/SKILL.md": SKILL_TEXT.format("ponytail"),
                  "skills/ponytail-review/SKILL.md": SKILL_TEXT.format("ponytail-review"),
                  "hooks/ponytail-activate.js": "", "hooks/ponytail-subagent.js": "",
                  "hooks/ponytail-mode-tracker.js": "",
                  "hooks/ponytail-instructions.js": "exports.getPonytailInstructions = m => 'RULES ' + m;\n",
                  ".opencode/command/ponytail-review.md": "Review.\n"}
CAVEMAN_FILES = {"skills/cavecrew/SKILL.md": SKILL_TEXT.format("cavecrew"),
                 "skills/caveman-explore/SKILL.md": SKILL_TEXT.format("caveman-explore"),
                 "skills/caveman/SKILL.md": SKILL_TEXT.format("caveman"),
                 "agents/cavecrew-investigator.md": "Investigate.\n", "agents/agents.json": "{}\n"}


def git(folder, *args):
    done = subprocess.run(["git", *GIT_OPTIONS, "-C", str(folder), *args], capture_output=True, text=True,
                          timeout=TIMEOUT)
    if done.returncode != 0:
        raise AssertionError(f"git {args[0]}: {done.stderr}")
    return done.stdout.strip()


def tagged_release(folder, tag, files):
    for name, text in files.items():
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text, encoding=ENCODING)
    if not (folder / ".git").is_dir():
        git(folder, "init", "-q")
    git(folder, "add", "-A")
    git(folder, "commit", "-q", "-m", tag)
    git(folder, "tag", "-a", tag, "-m", tag)


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
        self.opencode = self.root / "opencode"
        shutil.copytree(TOOLS, self.source / "tools", ignore=shutil.ignore_patterns("tests", "__pycache__"))
        (self.source / ".gitignore").write_text(IGNORED, encoding=ENCODING)
        git(self.source, "init", "-q")
        self.write_skill("alpha")
        self.commit("start", "tools", ".gitignore", "alpha")
        git(self.source, "tag", "-a", "v1.0.0", "-m", "v1.0.0")
        git(self.root, "clone", "-q", "--bare", str(self.source), str(self.origin))
        git(self.source, "remote", "add", "origin", str(self.origin))
        git(self.root, "clone", "-q", str(self.origin), str(self.clone))
        self.ponytail = self.root / "ponytail-source"
        self.xdg = self.root / "xdg"
        self.caveman = self.root / "caveman-source"
        self.ponytail_release("v5.0.0", PONYTAIL_FILES)
        self.caveman_release("v4.0.0", CAVEMAN_FILES)

    def ponytail_release(self, tag, files):
        tagged_release(self.ponytail, tag, files)

    def caveman_release(self, tag, files):
        tagged_release(self.caveman, tag, files)

    def write_skill(self, name, command=None):
        folder = self.source / name / "commands"
        folder.mkdir(parents=True, exist_ok=True)
        (folder.parent / "SKILL.md").write_text(SKILL_TEXT.format(name), encoding=ENCODING)
        (folder / f"{name}.md").write_text(command or COMMAND_TEXT.format(name), encoding=ENCODING)

    def commit(self, message, *paths):
        git(self.source, "add", "--", *paths)
        git(self.source, "commit", "-q", "-m", message)

    def push(self, message, *paths):
        self.commit(message, *paths)
        git(self.source, "push", "-q", "origin", BRANCH)

    def release(self, tag):
        git(self.source, "tag", "-a", tag, "-m", tag)
        git(self.source, "push", "-q", "origin", tag)

    def publish(self, message, *paths, tag="v1.1.0"):
        self.push(message, *paths)
        self.release(tag)

    def publish_removal(self, name, tag="v1.1.0"):
        git(self.source, "rm", "-r", "-q", name)
        git(self.source, "commit", "-q", "-m", f"remove {name}")
        git(self.source, "push", "-q", "origin", BRANCH)
        self.release(tag)

    def run(self, script, *args, path=None, tools=None, fresh=True):
        if fresh:
            (self.clone / ".ia" / "update-check.stamp").unlink(missing_ok=True)
        env = {key: value for key, value in os.environ.items() if key != SESSION_VAR}
        env[CONFIG_VAR] = str(self.config)
        env["CLAUDE_SKILLS_OPENCODE_DIR"] = str(self.opencode)
        env["CLAUDE_SKILLS_PONYTAIL_URL"] = self.ponytail.as_uri()
        env["CLAUDE_SKILLS_CAVEMAN_URL"] = self.caveman.as_uri()
        env["XDG_CONFIG_HOME"] = str(self.xdg)
        env["CLAUDE_SKILLS_GRAPHIFY_INDEX"] = (self.root / "no-index.json").as_uri()
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
