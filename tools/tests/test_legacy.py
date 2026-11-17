import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from legacy_world import ENCODING, MINE, UV, LegacyBase, done
from links import is_link


class LegacyTest(LegacyBase):
    def test_old_things_go_and_the_rest_stays(self):
        lines, _ = self.run_clean()
        for text in ("ponytail skill ponytail: removed", "caveman skill cavecrew: removed",
                     "caveman agent cavecrew-builder.md: removed", "ponytail opencode command ponytail.md: removed",
                     "ponytail opencode rules: removed", "ponytail mode: removed", "ponytail: removed",
                     "caveman: removed", "graphify skill: removed", "ponytail hook SessionStart: removed",
                     "ponytail hook SubagentStart: removed"):
            self.assertIn(text, lines)
        self.assertFalse((self.config / "ponytail").exists())
        self.assertFalse((self.config / "caveman").exists())
        self.assertFalse((self.config / "skills" / "graphify").exists())
        self.assertFalse((self.xdg / "ponytail").exists())
        self.assertFalse(os.path.lexists(self.config / "skills" / "ponytail"))
        self.assertFalse((self.opencode / "commands" / "ponytail.md").exists())
        self.assertFalse((self.opencode / "ponytail-ultra.md").exists())
        for name in ("ponytail.json", "caveman.json", "graphify.json", "graphify.log"):
            self.assertFalse(self.state(name).exists(), name)
        instructions = json.loads((self.opencode / "opencode.json").read_text(encoding=ENCODING))
        self.assertEqual(instructions["instructions"], ["keep.md"])
        settings = json.loads((self.config / "settings.json").read_text(encoding=ENCODING))
        self.assertEqual(settings, {"theme": "dark", "hooks": {"SessionStart": [MINE]}})

    def test_what_is_not_ours_stays_with_one_line(self):
        lines, _ = self.run_clean()
        self.assertTrue(is_link(self.config / "skills" / "ponytail-help"))
        self.assertTrue(self.other.is_file())
        self.assertEqual(self.reviewer.read_text(encoding=ENCODING), "edited by hand\n")
        self.assertIn("caveman agent cavecrew-reviewer.md: changed by hand, left as is", lines)
        self.assertTrue(any("ponytail skill ponytail-help" in line and "left as is" in line for line in lines))

    def test_second_run_prints_nothing(self):
        self.run_clean()
        lines, runner = self.run_clean()
        self.assertEqual(lines, [])
        runner.assert_not_called()

    def test_graphify_folder_without_the_mark_stays(self):
        (self.config / "skills" / "graphify" / ".claude-skills").unlink()
        lines, _ = self.run_clean()
        self.assertTrue((self.config / "skills" / "graphify").is_dir())
        self.assertNotIn("graphify skill: removed", lines)

    def test_mode_file_keeps_the_other_keys(self):
        path = self.write(self.xdg / "ponytail" / "config.json", '{"defaultMode": "ultra", "other": 1}')
        self.run_clean()
        self.assertEqual(json.loads(path.read_text(encoding=ENCODING)), {"other": 1})

    def test_other_mode_is_left_alone(self):
        path = self.write(self.xdg / "ponytail" / "config.json", '{"defaultMode": "lite"}')
        self.run_clean()
        self.assertTrue(path.is_file())

    def test_uv_uninstalls_the_package_when_it_lists_it(self):
        runner = mock.Mock(side_effect=lambda command: done(0, "graphifyy v1\n") if "list" in command else done())
        lines, runner = self.run_clean(which=UV, runner=runner)
        self.assertIn("graphify package: removed", lines)
        self.assertEqual(runner.call_args_list[-1].args[0], [UV, "tool", "uninstall", "graphifyy"])

    def test_pip_is_used_when_it_shows_the_package(self):
        runner = mock.Mock(side_effect=lambda command: done(0) if "show" in command or "uninstall" in command
                           else done(1))
        lines, runner = self.run_clean(runner=runner)
        self.assertIn("graphify package: removed", lines)
        self.assertEqual(runner.call_args_list[-1].args[0][1:], ["-m", "pip", "uninstall", "-y", "graphifyy"])

    def test_package_not_installed_means_no_line(self):
        lines, _ = self.run_clean()
        self.assertFalse(any("package" in line for line in lines))
        self.assertFalse(self.state("graphify.json").exists())

    def test_failure_keeps_the_registry_for_the_next_run(self):
        runner = mock.Mock(side_effect=subprocess.TimeoutExpired("pip", 1))
        lines, _ = self.run_clean(runner=runner)
        self.assertTrue(any(line.startswith("graphify package: not removed") for line in lines))
        self.assertTrue(self.state("graphify.json").is_file())
        self.assertFalse(self.state("ponytail.json").exists())
        self.run_clean()
        self.assertFalse(self.state("graphify.json").exists())

    def test_hooks_go_even_without_a_registry(self):
        for name in ("ponytail.json", "caveman.json", "graphify.json"):
            self.state(name).unlink()
        lines, _ = self.run_clean()
        self.assertEqual(len(lines), 2)
        self.assertTrue((self.config / "ponytail").is_dir())
        self.assertTrue(self.other.is_file())

    def test_broken_settings_are_left_alone(self):
        path = self.write(self.config / "settings.json", "{broken")
        self.run_clean()
        self.assertEqual(path.read_text(encoding=ENCODING), "{broken")


if __name__ == "__main__":
    unittest.main()
