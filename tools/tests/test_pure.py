import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import os
from unittest import mock

import board
import opencode_ponytail
import update
from hook import add_hooks
from paths import command_files, config_dir, skill_names
from registry import file_hash, read_json, write_json
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


class TempTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding=ENCODING)
        return path


class QuietTest(unittest.TestCase):
    def test_nothing_new_is_not_printed(self):
        for line in ("up to date (v1.6.2)", "ponytail: up to date (v5.0.0)", "skill alpha: already there",
                     "progress-board: http://127.0.0.1:8790 already running, starts at every login"):
            self.assertTrue(update.QUIET.fullmatch(line), line)

    def test_changes_and_failures_are_printed(self):
        for line in ("updated v1.0.0 to v1.1.0: beta", "could not install v1.1.0: blocked", "skill beta: linked",
                     "progress-board: http://127.0.0.1:8790 started, starts at every login"):
            self.assertIsNone(update.QUIET.fullmatch(line), line)


class NetworkDueTest(TempTest):
    def test_once_then_again_after_the_delay(self):
        stamp = self.root / ".ia" / "update-check.stamp"
        self.assertTrue(update.network_due(stamp))
        self.assertFalse(update.network_due(stamp))
        self.assertTrue(update.network_due(stamp, now=stamp.stat().st_mtime + update.CHECK_SECONDS + 1))


class StaleHookTest(TempTest):
    def test_hook_whose_script_left_is_removed(self):
        command = {"type": "command", "command": "node /x/ponytail/hooks/ponytail-subagent.js"}
        settings = self.write(self.root / "config" / "settings.json",
                              json.dumps({"hooks": {"SubagentStart": [{"hooks": [command]}]}}))
        lines = [text for _, text in add_hooks(self.root / "config", self.root / "config" / "claude-skills")]
        self.assertIn("ponytail subagent hook: removed", lines)
        self.assertNotIn("SubagentStart", json.loads(settings.read_text(encoding=ENCODING))["hooks"])
        self.assertFalse(any(line.endswith(": none") for line in lines))


class OpencodeCommandsTest(TempTest):
    def setUp(self):
        super().setUp()
        self.checkout, self.folder = self.root / "ponytail", self.root / "opencode"
        self.source = self.write(self.checkout / ".opencode" / "command" / "keep.md", "new\n")
        self.keep = self.write(self.folder / "commands" / "keep.md", "old\n")
        self.gone = self.write(self.folder / "commands" / "gone.md", "gone\n")
        self.registry = {"opencode_commands": {"keep.md": file_hash(self.keep), "gone.md": file_hash(self.gone)}}
        patches = (mock.patch.dict(os.environ, {"CLAUDE_SKILLS_OPENCODE_DIR": str(self.folder)}),
                   mock.patch.object(opencode_ponytail, "ultra_rules", return_value=None),
                   mock.patch("sync.shutil.copyfile", side_effect=OSError("locked")))
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def test_failed_copy_keeps_the_file_and_dropped_command_goes(self):
        lines = []
        opencode_ponytail.sync_opencode(self.checkout, self.registry, lines)
        self.assertTrue(self.keep.is_file())
        self.assertFalse(self.gone.exists())
        self.assertIn((False, "command opencode keep.md: not copied (locked)"), lines)
        self.assertEqual(sorted(self.registry["opencode_commands"]), ["keep.md"])

    def test_locked_dropped_command_is_reported(self):
        lines = []
        with mock.patch.object(Path, "unlink", side_effect=OSError("locked")):
            opencode_ponytail.sync_opencode(self.checkout, self.registry, lines)
        self.assertTrue(self.gone.is_file())
        self.assertIn((False, "command opencode gone.md: not removed (locked)"), lines)


class BoardTest(TempTest):
    def test_no_server_means_nothing_to_do(self):
        self.assertEqual(board.sync_board(self.root), [])
        self.assertEqual(board.unsync_board(self.root), [])

    def test_desktop_entry_quotes_each_argument(self):
        with mock.patch.object(board.sys, "platform", "linux"):
            text = board.autostart_text(["/usr/bin/python3", "-I", "/a b/server.py"])
        self.assertIn('Exec="/usr/bin/python3" "-I" "/a b/server.py"', text)

    def test_windows_run_key_is_written_and_dropped(self):
        key = mock.MagicMock()
        fake = mock.MagicMock(OpenKey=mock.MagicMock(return_value=key), DeleteValue=mock.MagicMock(
            side_effect=FileNotFoundError))
        key.__enter__.return_value = key
        self.write(self.root / "progress-board" / "server.py", "")
        with mock.patch.object(board.os, "name", "nt"), mock.patch.dict("sys.modules", {"winreg": fake}):
            board.set_autostart(["C:/py/pythonw.exe", "-I", "C:/a b/server.py"])
            lines = board.unsync_board(self.root)
        self.assertEqual(fake.SetValueEx.call_args.args[-1], 'C:/py/pythonw.exe -I "C:/a b/server.py"')
        self.assertIn("no longer starts at login", lines[0][1])


if __name__ == "__main__":
    unittest.main()
