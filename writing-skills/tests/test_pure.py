import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

from common import CHECK, NOTE, REFUSE
from companions import check_command_text, check_readme_text
from frontmatter import split
from shape import classify, crowded_headings, french_share
from skillmd import check_body, check_description

GOOD = "Use when a CSV must open in Excel, or when the user types /csv."
FRENCH = "Cette skill sert quand le fichier est ouvert dans Excel et que les dates sont fausses pour Marie."
ENGLISH = "This skill is used when the file is opened in Excel and the dates are wrong for the user."
COMMAND = """---
description: Ouvre la skill csv.
argument-hint: "[fichier]"
allowed-tools: Read,Skill
---
Charge la skill avec Skill, sinon $CLAUDE_CONFIG_DIR/skills/csv/SKILL.md puis ~/.claude/skills/csv/SKILL.md.
$ARGUMENTS donne le fichier.
"""


def levels(found):
    return sorted(item[0] for item in found)


def body(text):
    fields, lines, offset = split(text)
    return classify(lines, offset + 1)


class FrontMatter(unittest.TestCase):
    def test_reads_folded_description(self):
        fields, lines, offset = split("---\nname: csv\ndescription: >\n  Use when\n  a CSV breaks\n---\n# Csv\n")
        self.assertEqual(fields, {"name": "csv", "description": "Use when a CSV breaks"})
        self.assertEqual((lines, offset), (["# Csv"], 6))

    def test_no_front_matter(self):
        self.assertIsNone(split("# Title\n")[0])


class Description(unittest.TestCase):
    def test_triggers_only_pass(self):
        self.assertEqual(check_description(GOOD, ["csv"], 3), [])

    def test_missing_start_and_command(self):
        found = check_description("Handles CSV files for Excel.", ["csv"], 3)
        self.assertEqual(levels(found), [REFUSE, REFUSE])

    def test_workflow_is_flagged(self):
        found = check_description("Use when a fail-then-success CSV breaks: read it, then fix it.", [], 3)
        self.assertEqual(levels(found), [CHECK])

    def test_length_limit(self):
        found = check_description("Use when " + "a" * 1100, [], 3)
        self.assertIn(REFUSE, levels(found))

    def test_first_person(self):
        self.assertEqual(levels(check_description("Use when I export a CSV.", [], 3)), [CHECK])


class Shape(unittest.TestCase):
    def test_list_right_under_heading(self):
        rows = classify(["## Rules", "- one", "", "## Files", "Two files.", "- a", "## Flags", "| a |"])
        self.assertEqual(crowded_headings(rows), [(1, "list"), (7, "table")])

    def test_heading_inside_fence_is_code(self):
        rows = classify(["````markdown", "## Rules", "- one", "````"])
        self.assertEqual(crowded_headings(rows), [])

    def test_language_share(self):
        self.assertGreater(french_share(FRENCH), 0.5)
        self.assertLess(french_share(ENGLISH), 0.5)


class Body(unittest.TestCase):
    def test_complete_body_passes(self):
        text = "# Csv\n\n## Overview\n\nWhat.\n\n## Red flags\n\nTable.\n\n| Thought | Reality |\n\n## Files\n\nOne.\n"
        self.assertEqual(check_body(body(text), 15), [])

    def test_missing_overview_and_files_last(self):
        found = check_body(body("# Csv\n\n## Files\n\nOne.\n\n## Notes\n\nMore.\n"), 9)
        self.assertEqual(levels(found), [NOTE, REFUSE])

    def test_length(self):
        self.assertEqual(levels(check_body(body("# Csv\n\n## Overview\n\nWhat.\n\n## Files\n\nOne.\n"), 600)), [REFUSE])


class Readme(unittest.TestCase):
    def test_draft_refuses_tested_section(self):
        text = f"# Csv\n\n{FRENCH}\n\n## Ce qui a été testé\n\nRien.\n"
        self.assertEqual(levels(check_readme_text(text, True)), [REFUSE])

    def test_final_needs_tested_section(self):
        self.assertEqual(levels(check_readme_text(f"# Csv\n\n{FRENCH} Testé.\n", False)), [REFUSE])

    def test_final_untested_is_a_note(self):
        text = f"# Csv\n\n{FRENCH} Été.\n\n## Pas encore testé\n\nMarie a choisi.\n"
        self.assertEqual(levels(check_readme_text(text, False)), [NOTE])

    def test_english_and_missing(self):
        self.assertIn(CHECK, levels(check_readme_text(f"# Csv\n\n{ENGLISH} été\n", True)))
        self.assertEqual(levels(check_readme_text(None, True)), [REFUSE])


class Command(unittest.TestCase):
    def test_good_command(self):
        self.assertEqual(check_command_text("csv.md", COMMAND, "csv"), [])

    def test_accent_and_name(self):
        found = check_command_text("Créer.md", COMMAND.replace("Ouvre", "Crée"), "csv")
        self.assertEqual(levels(found), [REFUSE, REFUSE])

    def test_missing_fallback_skill_and_arguments(self):
        text = COMMAND.replace("Read,Skill", "Read").replace("~/.claude/", "").replace("$ARGUMENTS", "x")
        self.assertEqual(len(check_command_text("csv.md", text, "csv")), 3)


if __name__ == "__main__":
    unittest.main()
