import os
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from links import same_path
from world import World


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        self.world.run("install.py")

    def test_nothing_new(self):
        done = self.world.run("update.py")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("up to date (v1.0.0)", done.stdout)

    def test_new_release_brings_a_skill(self):
        self.world.write_skill("beta")
        self.world.publish("add beta", "beta")
        done = self.world.run("update.py")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("updated v1.0.0 to v1.1.0: beta", done.stdout)
        self.assertTrue(same_path(self.world.skill_link("beta"), self.world.clone / "beta"))
        self.assertTrue(self.world.command("beta.md").is_file())

    def test_push_without_release_is_ignored(self):
        self.world.write_skill("beta")
        self.world.push("add beta", "beta")
        done = self.world.run("update.py")
        self.assertIn("up to date (v1.0.0)", done.stdout)
        self.assertFalse(os.path.lexists(self.world.skill_link("beta")))

    def test_highest_version_wins(self):
        self.world.write_skill("beta")
        self.world.publish("add beta", "beta", tag="v1.10.0")
        self.world.write_skill("gamma")
        self.world.publish("add gamma", "gamma", tag="v1.9.0")
        done = self.world.run("update.py")
        self.assertIn("to v1.10.0", done.stdout)
        self.assertFalse(os.path.lexists(self.world.skill_link("gamma")))

    def test_second_run_finds_nothing(self):
        self.world.write_skill("beta")
        self.world.publish("add beta", "beta")
        self.world.run("update.py")
        done = self.world.run("update.py")
        self.assertIn("up to date (v1.1.0)", done.stdout)

    def test_removed_skill_goes_with_its_command(self):
        self.world.publish_removal("alpha")
        done = self.world.run("update.py")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("skill alpha: removed", done.stdout)
        self.assertFalse(os.path.lexists(self.world.skill_link("alpha")))
        self.assertFalse(self.world.command("alpha.md").exists())


if __name__ == "__main__":
    unittest.main()
