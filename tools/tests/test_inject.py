import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import inject

ENCODING = "utf-8"
TIMEOUT = 30
SPEECH = "---\nname: terse-speech\ndescription: x\n---\n\n# Speech\n\nShort.\n"
CODE = "# Code\n\nLess.\n"


class InjectTest(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.repo)

    def skill(self, name, text):
        (self.repo / name).mkdir()
        (self.repo / name / "SKILL.md").write_text(text, encoding=ENCODING)

    def test_front_matter_is_stripped(self):
        self.assertEqual(inject.strip_front_matter(SPEECH), "# Speech\n\nShort.")
        self.assertEqual(inject.strip_front_matter(CODE), "# Code\n\nLess.")

    def test_unclosed_front_matter_is_kept(self):
        self.assertEqual(inject.strip_front_matter("---\nname: x\n"), "---\nname: x")

    def test_both_bodies_in_one_message(self):
        self.skill("terse-speech", SPEECH)
        self.skill("least-code", CODE)
        found = inject.payload(self.repo, "SessionStart")
        self.assertEqual(list(found), ["hookSpecificOutput"])
        output = found["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        self.assertEqual(output["additionalContext"], "# Speech\n\nShort.\n\n# Code\n\nLess.")

    def test_missing_file_is_skipped(self):
        self.skill("least-code", CODE)
        found = inject.payload(self.repo, "SubagentStart")
        self.assertEqual(found["hookSpecificOutput"]["additionalContext"], "# Code\n\nLess.")

    def test_nothing_found_gives_an_empty_object(self):
        self.assertEqual(inject.payload(self.repo, "SessionStart"), {})

    def test_event_comes_from_stdin_then_argument(self):
        self.assertEqual(inject.event_name('{"hook_event_name": "SubagentStart"}', ["SessionStart"]), "SubagentStart")
        self.assertEqual(inject.event_name("", ["SessionStart"]), "SessionStart")
        self.assertEqual(inject.event_name("not json", ["SessionStart"]), "SessionStart")
        self.assertEqual(inject.event_name("[1]", []), "")


class InjectScriptTest(unittest.TestCase):
    def run_script(self, *args, stdin=None):
        return subprocess.run([sys.executable, "-I", str(TOOLS / "inject.py"), *args], capture_output=True,
                              text=True, input=stdin, stdin=None if stdin is not None else subprocess.DEVNULL,
                              timeout=TIMEOUT)

    def test_without_stdin_the_argument_is_used(self):
        done = self.run_script("SessionStart")
        self.assertEqual(done.returncode, 0, done.stderr)
        found = json.loads(done.stdout)
        self.assertTrue(found == {} or found["hookSpecificOutput"]["hookEventName"] == "SessionStart")

    def test_argument_wins_over_stdin(self):
        done = self.run_script("SessionStart", stdin='{"hook_event_name": "SubagentStart"}')
        found = json.loads(done.stdout)
        self.assertTrue(found == {} or found["hookSpecificOutput"]["hookEventName"] == "SessionStart")

    def test_stdin_event_used_without_argument(self):
        done = self.run_script(stdin='{"hook_event_name": "SubagentStart"}')
        found = json.loads(done.stdout)
        self.assertTrue(found == {} or found["hookSpecificOutput"]["hookEventName"] == "SubagentStart")

    def test_no_event_prints_an_empty_object(self):
        done = self.run_script()
        self.assertEqual(done.returncode, 0)
        self.assertEqual(json.loads(done.stdout), {})


if __name__ == "__main__":
    unittest.main()
