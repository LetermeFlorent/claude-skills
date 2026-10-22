import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

from push import ACCOUNTS_VAR, _command
from repo import GIT, GITHUB_KIND

ROOT = Path(tempfile.gettempdir()) / "work"
TARGET = {"kind": GITHUB_KIND, "owner": "someone", "url": "https://github.com/someone/repo.git"}
MISSING = Path(tempfile.gettempdir()) / "claude-skills-no-such-tool"


class PushCommandTest(unittest.TestCase):
    def test_plain_push_without_the_account_tool(self):
        self.assertEqual(_command(ROOT, TARGET, ["push"], MISSING), [GIT, "push"])

    def test_plain_push_when_the_variable_is_unset_or_empty(self):
        for value in (None, ""):
            with mock.patch.dict(os.environ):
                os.environ.pop(ACCOUNTS_VAR, None)
                if value is not None:
                    os.environ[ACCOUNTS_VAR] = value
                self.assertEqual(_command(ROOT, TARGET, ["push"]), [GIT, "push"])

    def test_account_tool_named_by_the_variable(self):
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            tool = Path(handle.name)
        self.addCleanup(tool.unlink)
        with mock.patch.dict(os.environ, {ACCOUNTS_VAR: str(tool)}):
            command = _command(ROOT, TARGET, ["push"])
        self.assertEqual(command[1], str(tool))

    def test_account_tool_when_installed(self):
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            tool = Path(handle.name)
        self.addCleanup(tool.unlink)
        command = _command(ROOT, TARGET, ["push"], tool)
        self.assertEqual(command[1:4], [str(tool), "run", "github"])
        self.assertIn("someone", command)
        self.assertEqual(command[-1], "push")


if __name__ == "__main__":
    unittest.main()
