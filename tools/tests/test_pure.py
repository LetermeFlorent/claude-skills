import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from paths import command_files, config_dir, skill_names
from registry import read_json, write_json
from gitcalls import version

ENCODING = "utf-8"
TREE = {"alpha": ["SKILL.md", "commands/a.md", "commands/notes.txt"], "beta": ["SKILL.md"],
        "notes": ["commands/x.md"], "tools": ["update.py"]}


class ConfigDirTest(unittest.TestCase):
    def test_variable_wins(self):
        self.assertEqual(config_dir({"CLAUDE_CONFIG_DIR": "/srv/conf"}, "/home/a"), Path("/srv/conf"))

    def test_blank_variable_falls_back_to_home(self):
        self.assertEqual(config_dir({"CLAUDE_CONFIG_DIR": "  "}, "/home/a"), Path("/home/a/.claude"))

    def test_home_by_default(self):
        self.assertEqual(config_dir({}, "/home/a"), Path("/home/a/.claude"))


class VersionTest(unittest.TestCase):
    def test_numbers_compare_as_numbers(self):
        self.assertGreater(version("v1.10.0"), version("v1.9.3"))

    def test_other_tags_are_not_releases(self):
        for tag in ("1.0.0", "v1.0", "v1.0.0-beta", "latest"):
            self.assertIsNone(version(tag))


class JsonTest(unittest.TestCase):
    def setUp(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder)
        self.path = folder / ".ia" / "state.json"

    def test_missing_file(self):
        self.assertEqual(read_json(self.path), {})

    def test_round_trip(self):
        write_json(self.path, {"session": "s1"})
        self.assertEqual(read_json(self.path), {"session": "s1"})

    def test_corrupt_file(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json", encoding=ENCODING)
        self.assertEqual(read_json(self.path), {})

    def test_list_is_not_a_registry(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[1, 2]", encoding=ENCODING)
        self.assertEqual(read_json(self.path), {})


class ListingTest(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.repo)
        for folder, names in TREE.items():
            for name in names:
                path = self.repo / folder / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x", encoding=ENCODING)

    def test_skill_folders_hold_a_skill_file(self):
        self.assertEqual(skill_names(self.repo), ["alpha", "beta"])

    def test_commands_come_from_skill_folders_only(self):
        found = command_files(self.repo)
        self.assertEqual(sorted(found), ["a.md"])
        self.assertEqual(found["a.md"], self.repo / "alpha" / "commands" / "a.md")


if __name__ == "__main__":
    unittest.main()
