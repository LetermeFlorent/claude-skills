import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "lib"))

import history
from files import kind_of
from markdown import drop_separators, nested_fences, separators, structure
from signatures import AI_BRANCH, AI_FILES, BOT_IDENTITY, LEFTOVER_FILES, TRAILER
from text import clean, fix_line, line_markers, safe_markers

CURLY_OPEN, CURLY_CLOSE, CURLY_APOSTROPHE = "\u201c", "\u201d", "\u2019"
EM_DASH, NO_BREAK, NARROW_NO_BREAK, ZERO_WIDTH = "\u2014", "\u00a0", "\u202f", "\u200b"
OPEN_GUILLEMET, CLOSE_GUILLEMET = "\u00ab", "\u00bb"
ROCKET = "\U0001F680"


class TrailerTest(unittest.TestCase):
    def test_tool_trailers_are_matched(self):
        lines = ("Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
                 "Co-authored-by: Codex <noreply@openai.com>",
                 "Co-authored-by: Cursor <cursoragent@cursor.com>",
                 "Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>",
                 "Made-with: Cursor", "Made with Cursor", "Agent-Logs-Url: https://example.org/run/1",
                 "Claude-Session: https://claude.ai/code/session_1",
                 "Generated with [Claude Code](https://claude.com/claude-code)")
        for line in lines:
            self.assertTrue(TRAILER.search(line), line)

    def test_a_person_named_claude_stays(self):
        self.assertIsNone(TRAILER.search("Co-authored-by: Claude Martin <claude.martin@example.fr>"))

    def test_bot_identities(self):
        self.assertTrue(BOT_IDENTITY.search("Marie (aider)"))
        self.assertTrue(BOT_IDENTITY.search("google-labs-jules[bot]"))
        self.assertIsNone(BOT_IDENTITY.search("Claude Martin"))

    def test_branches_named_after_a_tool(self):
        self.assertTrue(AI_BRANCH.search("codex/fix-login"))
        self.assertTrue(AI_BRANCH.search("refs/remotes/origin/claude/issue-3-20261022"))
        self.assertIsNone(AI_BRANCH.search("feature/login"))

    def test_tool_files_and_leftovers(self):
        self.assertTrue(AI_FILES.search("AGENTS.md"))
        self.assertTrue(AI_FILES.search(".github/copilot-instructions.md"))
        self.assertIsNone(AI_FILES.search("src/agent.py"))
        self.assertTrue(LEFTOVER_FILES.search("IMPLEMENTATION_SUMMARY.md"))
        self.assertIsNone(LEFTOVER_FILES.search("SUMMARY.md"))


class HistoryTest(unittest.TestCase):
    def test_clean_drops_tool_trailers_and_keeps_people(self):
        message = ("Update notes\n\nMade-with: Cursor\nCo-authored-by: Claude Martin <claude.martin@example.fr>\n"
                   "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n")
        expected = "Update notes\n\nCo-authored-by: Claude Martin <claude.martin@example.fr>\n"
        self.assertEqual(history.clean(message), expected)


class TextTest(unittest.TestCase):
    def test_clean_straightens_and_removes_invisible_characters(self):
        text = (f"{CURLY_OPEN}Oui{CURLY_CLOSE}, l{CURLY_APOSTROPHE}outil{NO_BREAK}: "
                f"{OPEN_GUILLEMET} simple {CLOSE_GUILLEMET}{ZERO_WIDTH}")
        self.assertEqual(clean(text), "\"Oui\", l'outil : \"simple\"")

    def test_fix_line_spares_inline_code(self):
        line = f"run `{CURLY_OPEN}x{CURLY_CLOSE}` then {CURLY_OPEN}y{CURLY_CLOSE}"
        fixed, kinds = fix_line(line)
        self.assertEqual(fixed, f"run `{CURLY_OPEN}x{CURLY_CLOSE}` then \"y\"")
        self.assertEqual(kinds, ["quotes"])

    def test_fix_line_leaves_clean_lines_alone(self):
        self.assertEqual(fix_line("plain text"), ("plain text", []))

    def test_line_markers_in_prose(self):
        found = line_markers(f"We delve into it {EM_DASH} done {ROCKET}", True)
        self.assertIn("vocabulary: delve", found)
        self.assertIn("em dash", found)
        self.assertIn("emoji", found)

    def test_line_markers_in_code_skip_vocabulary(self):
        self.assertEqual(line_markers("robust = True  # TODO: implement", False), ["placeholder: todo: implement"])

    def test_chatbot_residue(self):
        self.assertTrue(line_markers("see turn0search3 and [cite: 2]", True)[0].startswith("residue"))

    def test_safe_markers(self):
        self.assertEqual(safe_markers(f"Pourquoi{NARROW_NO_BREAK}?"), ["space"])


class MarkdownTest(unittest.TestCase):
    def test_separators_spare_front_matter_setext_and_fences(self):
        lines = ["---", "title: x", "---", "Heading", "---", "", "text", "", "---", "", "```", "", "---", "```"]
        self.assertEqual(separators(lines), [9])

    def test_drop_separators_keeps_one_blank_line(self):
        self.assertEqual(drop_separators(["a", "", "---", "", "b"], [3]), ["a", "", "b"])

    def test_structure(self):
        lines = ["# The Best Tool Ever", "- one", "", "## Usage notes", "", "Some text.", "- **Fast**: yes"]
        found = structure(lines)
        self.assertEqual(found["title case heading"], [1])
        self.assertEqual(found["list right under a heading"], [1])
        self.assertEqual(found["bold lead-in"], [7])

    def test_setext_headings_are_headings(self):
        self.assertEqual(structure(["Setext Title Here", "---", "", "Plain words here", ""]),
                         {"title case heading": [1]})

    def test_nested_fence_of_the_same_length(self):
        self.assertEqual(nested_fences(["```markdown", "```python", "x", "```", "```"]), [2])
        self.assertEqual(nested_fences(["````markdown", "```python", "x", "```", "````"]), [])


class KindTest(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(kind_of(Path("locales/fr.json")), "value")
        self.assertEqual(kind_of(Path("tests/fixtures/sample.md")), "value")
        self.assertEqual(kind_of(Path("README.md")), "prose")
        self.assertEqual(kind_of(Path("src/app.py")), "code")
        self.assertEqual(kind_of(Path("report.pdf")), "document")


if __name__ == "__main__":
    unittest.main()
