import os
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from world import ENCODING, World, git


class RefusalTest(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        self.world.run("install.py")
        self.world.write_skill("beta")
        self.world.publish("add beta", "beta")

    def test_local_changes_block_the_update(self):
        (self.world.clone / "alpha" / "SKILL.md").write_text("edited\n", encoding=ENCODING)
        done = self.world.run("update.py", session="s1")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("local changes: not updated", done.stdout)
        self.assertFalse(os.path.lexists(self.world.skill_link("beta")))

    def test_local_commits_block_the_update(self):
        (self.world.clone / "notes.md").write_text("mine\n", encoding=ENCODING)
        git(self.world.clone, "add", "--", "notes.md")
        git(self.world.clone, "commit", "-q", "-m", "local")
        done = self.world.run("update.py", session="s1")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("local commits: not updated", done.stdout)
        self.assertFalse(os.path.lexists(self.world.skill_link("beta")))

    def test_unreachable_remote_keeps_the_copy(self):
        git(self.world.clone, "remote", "set-url", "origin", str(self.world.root / "missing.git"))
        done = self.world.run("update.py", session="s1")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("could not reach GitHub: kept ", done.stdout)
        again = self.world.run("update.py", session="s1")
        self.assertEqual(again.stdout.strip(), "already checked this session")

    def test_missing_git_skips_the_update(self):
        empty = self.world.root / "empty"
        empty.mkdir()
        done = self.world.run("update.py", session="s1", path=empty)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("git not found: update skipped", done.stdout)

    def test_hand_edited_command_is_left_alone(self):
        self.world.command("alpha.md").write_text("mine\n", encoding=ENCODING)
        self.world.write_skill("alpha", command="Read alpha twice.\n")
        self.world.publish("change alpha", "alpha")
        done = self.world.run("update.py", session="s1")
        self.assertIn("command alpha.md: changed by hand", done.stdout)
        self.assertEqual(self.world.command("alpha.md").read_text(encoding=ENCODING), "mine\n")

    def test_unexpected_error_is_one_line(self):
        (self.world.clone / ".ia" / "update.json").mkdir(parents=True)
        done = self.world.run("update.py", session="s1")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("claude-skills: ", done.stdout)
        self.assertNotIn("Traceback", done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
