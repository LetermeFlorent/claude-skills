import json
import os
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from links import is_link, make_link, remove_link, same_path
from world import COMMAND_TEXT, ENCODING, World


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)

    def test_links_skill_and_copies_command(self):
        done = self.world.run("install.py")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("skill alpha: linked", done.stdout)
        self.assertTrue(same_path(self.world.skill_link("alpha"), self.world.clone / "alpha"))
        self.assertEqual(self.world.command("alpha.md").read_text(encoding=ENCODING), COMMAND_TEXT.format("alpha"))

    def test_second_run_finds_everything_in_place(self):
        self.world.run("install.py")
        done = self.world.run("install.py")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("skill alpha: already there", done.stdout)
        self.assertIn("command alpha.md: already there", done.stdout)

    def test_lost_registry_adopts_identical_command(self):
        self.world.run("install.py")
        (self.world.clone / ".ia" / "installed.json").unlink()
        done = self.world.run("install.py")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("command alpha.md: already there", done.stdout)

    def test_foreign_folder_is_skipped_and_kept(self):
        foreign = self.world.skill_link("alpha")
        foreign.mkdir(parents=True)
        (foreign / "keep.txt").write_text("mine", encoding=ENCODING)
        done = self.world.run("install.py")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("skill alpha: skipped", done.stdout)
        self.assertTrue((foreign / "keep.txt").is_file())
        self.assertFalse(is_link(foreign))

    def test_file_in_place_of_skills_folder(self):
        (self.world.config / "skills").write_text("x", encoding=ENCODING)
        done = self.world.run("install.py")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("skill alpha: not linked", done.stdout)
        self.assertNotIn("Traceback", done.stdout + done.stderr)

    def test_uninstall_keeps_the_repository(self):
        self.world.run("install.py")
        done = self.world.run("install.py", "--uninstall")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertFalse(os.path.lexists(self.world.skill_link("alpha")))
        self.assertFalse(self.world.command("alpha.md").exists())
        self.assertTrue((self.world.clone / "alpha" / "SKILL.md").is_file())

    def test_uninstall_keeps_a_link_the_user_re_pointed(self):
        self.world.run("install.py")
        link, own = self.world.skill_link("alpha"), self.world.root / "own-alpha"
        own.mkdir()
        (own / "keep.txt").write_text("mine", encoding=ENCODING)
        remove_link(link)
        make_link(link, own)
        done = self.world.run("install.py", "--uninstall")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("skill alpha:", done.stdout)
        self.assertIn("points elsewhere, left as is", done.stdout)
        self.assertTrue(is_link(link))
        self.assertTrue(same_path(link, own))
        self.assertTrue((own / "keep.txt").is_file())

    def settings(self):
        return json.loads((self.world.config / "settings.json").read_text(encoding=ENCODING))

    def test_hooks_are_added_once_next_to_other_settings(self):
        (self.world.config / "settings.json").parent.mkdir(parents=True, exist_ok=True)
        (self.world.config / "settings.json").write_text('{"model": "opus"}', encoding=ENCODING)
        self.world.run("install.py")
        done = self.world.run("install.py")
        self.assertIn("update hook: already there", done.stdout)
        data = self.settings()
        self.assertEqual(data["model"], "opus")
        entries = data["hooks"]["SessionStart"]
        self.assertEqual(len(entries), 1)
        self.assertIn("claude-skills/tools/update.py", entries[0]["hooks"][0]["command"])
        guard = data["hooks"]["PreToolUse"]
        self.assertEqual(len(guard), 1)
        self.assertEqual(guard[0]["matcher"], "Bash")
        self.assertTrue(guard[0]["hooks"][0]["command"].endswith('resource-guard/scripts/guard.py" hook'))
        self.assertIn("resource hook: already there", done.stdout)

    def test_uninstall_removes_only_our_hooks(self):
        self.world.run("install.py")
        data = self.settings()
        data["hooks"]["SessionStart"].append({"hooks": [{"type": "command", "command": "mine"}]})
        (self.world.config / "settings.json").write_text(json.dumps(data), encoding=ENCODING)
        done = self.world.run("install.py", "--uninstall")
        self.assertIn("update hook: removed", done.stdout)
        self.assertIn("resource hook: removed", done.stdout)
        self.assertNotIn("PreToolUse", self.settings()["hooks"])
        mine = [{"hooks": [{"type": "command", "command": "mine"}]}]
        self.assertEqual(self.settings()["hooks"]["SessionStart"], mine)

    def test_broken_settings_are_left_alone(self):
        (self.world.config / "settings.json").parent.mkdir(parents=True, exist_ok=True)
        (self.world.config / "settings.json").write_text("{broken", encoding=ENCODING)
        done = self.world.run("install.py")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("update hook: not added", done.stdout)
        self.assertEqual((self.world.config / "settings.json").read_text(encoding=ENCODING), "{broken")

    def test_repository_in_the_wrong_place_is_refused(self):
        done = self.world.run("install.py", tools=self.world.source / "tools")
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("clone it into", done.stdout)


if __name__ == "__main__":
    unittest.main()
