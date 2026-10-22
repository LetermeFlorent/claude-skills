import os
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from gitcalls import top_folders
from links import same_path
from world import World

CHECKED = "already checked this session"


class TopFoldersTest(unittest.TestCase):
    def test_keeps_known_skill_folders(self):
        paths = ["alpha/SKILL.md", "alpha/commands/a.md", "tools/update.py", "README.md", "beta/x.py"]
        self.assertEqual(top_folders(paths, ["alpha", "beta", "gamma"]), ["alpha", "beta"])


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        self.world.run("install.py")

    def test_nothing_new(self):
        done = self.world.run("update.py", session="s1")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("up to date (", done.stdout)

    def test_new_skill_arrives(self):
        self.world.write_skill("beta")
        self.world.publish("add beta", "beta")
        done = self.world.run("update.py", session="s1")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn(": beta. Re-read the SKILL.md", done.stdout)
        self.assertTrue(same_path(self.world.skill_link("beta"), self.world.clone / "beta"))
        self.assertTrue(self.world.command("beta.md").is_file())

    def test_same_session_checks_once(self):
        self.world.run("update.py", session="s1")
        done = self.world.run("update.py", session="s1")
        self.assertEqual(done.stdout.strip(), CHECKED)

    def test_new_session_checks_again(self):
        self.world.run("update.py", session="s1")
        done = self.world.run("update.py", session="s2")
        self.assertIn("up to date (", done.stdout)

    def test_no_session_waits_twelve_hours(self):
        self.world.run("update.py")
        done = self.world.run("update.py")
        self.assertEqual(done.stdout.strip(), CHECKED)

    def test_removed_skill_goes_with_its_command(self):
        self.world.publish_removal("alpha")
        done = self.world.run("update.py", session="s1")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("skill alpha: removed", done.stdout)
        self.assertFalse(os.path.lexists(self.world.skill_link("alpha")))
        self.assertFalse(self.world.command("alpha.md").exists())


if __name__ == "__main__":
    unittest.main()
