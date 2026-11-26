import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import legacy
import legacy_graphify
from links import is_link, make_link, remove_link
from registry import file_hash, write_json

ENCODING = "utf-8"
OLD_HOOK = {"hooks": [{"type": "command", "command": "node /x/ponytail/hooks/ponytail-activate.js"}]}
MINE = {"hooks": [{"type": "command", "command": "mine"}]}
UV = "/bin/uv"
FAKE_HASH = "0" * 64


def done(code=0, out="", err=""):
    return SimpleNamespace(returncode=code, stdout=out, stderr=err)


def nothing_installed(command):
    return done(1)


class LegacyBase(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="claude skills legacy "))
        self.config, self.repo = self.root / "config", self.root / "config" / "claude-skills"
        self.opencode, self.xdg = self.root / "opencode", self.root / "xdg"
        self.links = []
        self.addCleanup(self.close)
        patch = mock.patch.dict(os.environ, {"CLAUDE_SKILLS_OPENCODE_DIR": str(self.opencode),
                                             "CLAUDE_SKILLS_QWEN_DIR": str(self.root / "qwen"),
                                             "XDG_CONFIG_HOME": str(self.xdg)})
        patch.start()
        self.addCleanup(patch.stop)
        self.build()

    def close(self):
        for link in self.links:
            if is_link(link):
                remove_link(link)
        shutil.rmtree(self.root)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding=ENCODING)
        return path

    def link(self, name, target):
        target.mkdir(parents=True, exist_ok=True)
        make_link(self.config / "skills" / name, target)
        self.links.append(self.config / "skills" / name)

    def state(self, name):
        return self.repo / ".ia" / name

    def build(self):
        self.write(self.config / "ponytail" / ".git" / "HEAD", "x")
        self.write(self.config / "caveman" / ".git" / "HEAD", "x")
        self.link("ponytail", self.config / "ponytail" / "skills" / "ponytail")
        self.link("cavecrew", self.config / "caveman" / "skills" / "cavecrew")
        self.link("ponytail-help", self.root / "elsewhere")
        builder = self.write(self.config / "agents" / "cavecrew-builder.md", "builder\n")
        self.reviewer = self.write(self.config / "agents" / "cavecrew-reviewer.md", "edited by hand\n")
        self.other = self.write(self.config / "agents" / "mine.md", "mine\n")
        command = self.write(self.opencode / "commands" / "ponytail.md", "cmd\n")
        rules = self.write(self.opencode / "ponytail-ultra.md", "rules\n")
        self.write(self.opencode / "opencode.json", json.dumps({"instructions": [rules.as_posix(), "keep.md"]}))
        self.write(self.xdg / "ponytail" / "config.json", '{"defaultMode": "ultra"}')
        self.write(self.config / "skills" / "graphify" / ".claude-skills", "")
        self.write(self.config / "settings.json", json.dumps({"theme": "dark", "hooks": {
            "SessionStart": [OLD_HOOK, MINE], "SubagentStart": [OLD_HOOK]}}))
        write_json(self.state("ponytail.json"), {"skills": ["ponytail", "ponytail-help"], "opencode_rules":
                   rules.as_posix(), "opencode_commands": {"ponytail.md": file_hash(command)}})
        write_json(self.state("caveman.json"), {"skills": ["cavecrew"], "agents": {
            "cavecrew-builder.md": file_hash(builder), "cavecrew-reviewer.md": FAKE_HASH}})
        write_json(self.state("graphify.json"), {"version": "1"})
        self.write(self.state("graphify.log"), "log")

    def run_clean(self, which="/bin/missing", runner=None):
        runner = runner or mock.Mock(side_effect=nothing_installed)
        with mock.patch.object(legacy_graphify.shutil, "which", return_value=which), \
                mock.patch.object(legacy_graphify, "run", runner):
            return [text for _, text in legacy.clean(self.repo, self.config)], runner
