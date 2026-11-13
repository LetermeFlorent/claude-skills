import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from links import same_path
from world import ENCODING, World


class PonytailTest(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        self.checkout = self.world.config / "ponytail"

    def read(self, path):
        return json.loads(Path(path).read_text(encoding=ENCODING))

    def test_install_brings_ponytail_at_ultra(self):
        done = self.world.run("install.py")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("ponytail: installed v5.0.0", done.stdout)
        target = self.checkout / "skills" / "ponytail-review"
        self.assertTrue(same_path(self.world.skill_link("ponytail-review"), target))
        self.assertEqual(self.read(self.world.xdg / "ponytail" / "config.json")["defaultMode"], "ultra")
        hooks = self.read(self.world.config / "settings.json")["hooks"]
        self.assertIn("ponytail/hooks/ponytail-activate.js", json.dumps(hooks["SessionStart"]))
        self.assertNotIn("matcher", hooks["UserPromptSubmit"][0])
        self.assertTrue((self.world.opencode / "commands" / "ponytail-review.md").is_file())

    def test_opencode_gets_the_ultra_rules(self):
        self.world.run("install.py")
        rules = self.world.opencode / "ponytail-ultra.md"
        if not rules.is_file():
            self.skipTest("node not found")
        self.assertEqual(rules.read_text(encoding=ENCODING), "RULES ultra")
        self.assertEqual(self.read(self.world.opencode / "opencode.json")["instructions"], [rules.as_posix()])

    def test_mode_is_put_back_to_ultra(self):
        self.world.run("install.py")
        (self.world.xdg / "ponytail" / "config.json").write_text('{"defaultMode": "lite"}', encoding=ENCODING)
        done = self.world.run("update.py")
        self.assertIn("ponytail mode ultra: set", done.stdout)
        self.assertNotIn("ponytail mode", self.world.run("update.py").stdout)

    def test_mode_is_put_back_between_network_checks(self):
        self.world.run("update.py")
        mode = self.world.xdg / "ponytail" / "config.json"
        mode.write_text('{"defaultMode": "lite"}', encoding=ENCODING)
        done = self.world.run("update.py", fresh=False)
        self.assertIn("ponytail mode ultra: set", done.stdout)
        self.assertEqual(self.read(mode)["defaultMode"], "ultra")

    def test_new_ponytail_release_is_installed(self):
        self.world.run("install.py")
        self.world.ponytail_release("v5.1.0", {"skills/ponytail-gain/SKILL.md": "---\nname: g\n---\n"})
        done = self.world.run("update.py")
        self.assertIn("ponytail: updated v5.0.0 to v5.1.0", done.stdout)
        self.assertIn("skill ponytail-gain: linked", done.stdout)
        self.assertNotIn("ponytail: ", self.world.run("update.py").stdout)

    def test_foreign_folder_is_left_alone(self):
        self.checkout.mkdir(parents=True)
        done = self.world.run("install.py")
        self.assertIn("is not ours, left as is", done.stdout)
        self.assertNotIn("ponytail-activate", (self.world.config / "settings.json").read_text(encoding=ENCODING))

    def test_uninstall_takes_ponytail_away(self):
        self.world.run("install.py")
        done = self.world.run("install.py", "--uninstall")
        self.assertIn("ponytail: removed", done.stdout)
        self.assertFalse(self.checkout.exists())
        self.assertFalse(self.world.skill_link("ponytail").exists())
        self.assertFalse((self.world.opencode / "commands" / "ponytail-review.md").exists())
        self.assertNotIn("ponytail", (self.world.config / "settings.json").read_text(encoding=ENCODING))


if __name__ == "__main__":
    unittest.main()
