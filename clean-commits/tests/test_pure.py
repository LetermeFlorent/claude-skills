import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

from push import _command
from repo import GIT, GITHUB_KIND

ROOT = Path(tempfile.gettempdir()) / "work"
TARGET = {"kind": GITHUB_KIND, "owner": "someone", "url": "https://github.com/someone/repo.git"}
MISSING = Path(tempfile.gettempdir()) / "claude-skills-no-such-tool"


class PushCommandTest(unittest.TestCase):
    def test_plain_push_without_the_account_tool(self):
        self.assertEqual(_command(ROOT, TARGET, ["push"], MISSING), [GIT, "push"])

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
