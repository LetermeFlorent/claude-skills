import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

import resume_check
import resume_file
from common import MARKER

AGENT = """## Agent a1 : fix the build

Type: general-purpose. Model: sonnet. Effort: medium. Depth: 1.
Answer at stop: yes, at 10:00
Status: done
To relaunch: no, because finished
Relaunch order: none
Files it owns: none

### Starting brief

````text
Fix the build.
````

### Its report

````text
AGENT REPORT
END REPORT
````
"""


def resume_text(state="STOPPED", agent=AGENT):
    return (f"{MARKER}\n# Stop-all resume\n\nState: {state}\n"
            "Stop requested on 2026-01-01 10:00, origin session sess1.\n\n" + agent)


class ResumeCheck(unittest.TestCase):
    def test_complete_file_is_ok(self):
        self.assertEqual(resume_check.check(resume_text(), ["a1"]), [])

    def test_missing_marker_state_and_agent(self):
        problems = resume_check.check("# Resume\n", ["a1"])
        self.assertEqual(len(problems), 3)

    def test_missing_field_and_empty_prompt(self):
        broken = AGENT.replace("Status: done\n", "").replace("Fix the build.\n", "")
        problems = resume_check.check(resume_text(agent=broken), ["a1"])
        self.assertIn("agent a1: missing 'Status:'", problems)
        self.assertIn("agent a1: original prompt block is empty", problems)

    def test_pending_only_blocks_a_finished_stop(self):
        pending = AGENT.replace("Status: done", "Status: pending a1")
        self.assertEqual(resume_check.check(resume_text("STOP IN PROGRESS", pending), ["a1"]), [])
        self.assertTrue(any("still pending" in p for p in resume_check.check(resume_text(agent=pending), [])))

    def test_lost_prompt_needs_a_note(self):
        lost = AGENT.replace("Fix the build.", "PROMPT NOT FOUND")
        self.assertTrue(any("not found" in p for p in resume_check.check(resume_text(agent=lost), [])))
        noted = lost + "\nBrief lost: transcript deleted\n"
        self.assertEqual(resume_check.check(resume_text(agent=noted), []), [])

    def test_headings_inside_code_blocks_are_ignored(self):
        quoted = AGENT.replace("AGENT REPORT", "AGENT REPORT\n## Agent zz")
        self.assertEqual(resume_check.agent_sections(resume_text(agent=quoted)).keys(), {"a1"})

    def test_forbidden_character_and_unclosed_block(self):
        dashed = resume_text() + "a " + chr(0x2014) + " b\n"
        self.assertTrue(any("em dash" in p for p in resume_check.check(dashed, [])))
        self.assertTrue(any("never closed" in p for p in resume_check.check(resume_text() + "````text\nx\n", [])))

    def test_template_placeholder_left(self):
        problems = resume_check.check(resume_text() + "Folder: <absolute path>\n", [])
        self.assertIn("template placeholder left: <absolute path>", problems)


class ResumeFile(unittest.TestCase):
    def test_describe(self):
        state, origin = resume_file.describe(resume_text())
        self.assertEqual((state, origin), ("State: STOPPED", "sess1"))
        self.assertEqual(resume_file.describe("nothing"), ("State: unknown", "unknown"))

    def test_scan_separates_ours_from_foreign(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "resume.md").write_text("user notes", encoding="utf-8")
            Path(folder, "resume-2026-01-01-1000.md").write_text(resume_text(), encoding="utf-8")
            ours, foreign = resume_file.scan(folder)
        self.assertEqual([os.path.basename(item[1]) for item in ours], ["resume-2026-01-01-1000.md"])
        self.assertEqual([os.path.basename(path) for path in foreign], ["resume.md"])
        self.assertEqual(ours[0][2:], ("State: STOPPED", "sess1"))

    def test_scan_of_an_empty_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(resume_file.scan(folder), ([], []))

    def test_candidate_dirs_start_with_ia_folder_and_skip_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, ".ia").mkdir()
            dirs = resume_file.candidate_dirs(folder)
            self.assertIn(str(Path(folder, ".ia")), dirs)
            self.assertEqual(len(dirs), len({os.path.normcase(d) for d in dirs}))
            self.assertTrue(all(os.path.isdir(d) for d in dirs))


if __name__ == "__main__":
    unittest.main()
