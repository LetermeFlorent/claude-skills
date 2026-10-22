import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

from common import CHECK, NOTE, REFUSE
from links import check_links, referenced
from pyrules import comment_lines, entry_findings, source_findings
from skillmd import check_lines

HASH = chr(35)
ENTRY = "import sys\nsys.dont_write_bytecode = True\nfrom common import guard\nguard(print, 'x')\n"


def levels(found):
    return sorted(item[0] for item in found)


def function(name, parameters, lines):
    return f"def {name}({parameters}):\n" + "    x = 1\n" * (lines - 1)


class Sources(unittest.TestCase):
    def test_clean_source(self):
        self.assertEqual(source_findings("a.py", function("run", "self, a, b, c, d", 3)), [])

    def test_comment_and_allowed_markers(self):
        text = f"{HASH}!/usr/bin/env python\nx = 1  {HASH} noqa\ny = 2  {HASH} why\n"
        self.assertEqual(comment_lines(text), [3])

    def test_hash_inside_string_is_not_a_comment(self):
        self.assertEqual(comment_lines(f"x = '{HASH} text'\n"), [])

    def test_long_function_and_parameters(self):
        found = source_findings("a.py", function("run", "a, b, c, *rest", 42))
        self.assertEqual(levels(found), [REFUSE])
        found = source_findings("a.py", function("run", "a, b, c, d, e", 3))
        self.assertEqual(levels(found), [REFUSE])

    def test_width_length_and_syntax(self):
        self.assertEqual(levels(source_findings("a.py", "x = '" + "a" * 130 + "'\n")), [REFUSE])
        self.assertEqual(levels(source_findings("a.py", "x = 1\n" * 151)), [REFUSE])
        self.assertEqual(levels(source_findings("a.py", "def (:\n")), [REFUSE])


class Entry(unittest.TestCase):
    def test_flag_before_local_import(self):
        self.assertEqual(entry_findings("scripts/a.py", ENTRY, {"common"}), [])

    def test_local_import_first(self):
        text = "from common import guard\nimport sys\nsys.dont_write_bytecode = True\nguard(print, 'x')\n"
        self.assertEqual(levels(entry_findings("scripts/a.py", text, {"common"})), [REFUSE])

    def test_no_guard(self):
        text = ENTRY.replace("guard(print, 'x')", "print('x')").replace("import guard", "import show")
        self.assertEqual(levels(entry_findings("scripts/a.py", text, {"common"})), [CHECK])


class Links(unittest.TestCase):
    def test_referenced_tokens(self):
        text = "Run `scripts/check.py`, read `reference/testing.md`, `subject-brief.md`, `<run>/tmp` and `git`."
        self.assertEqual(referenced(text), ["reference/testing.md", "scripts/check.py", "subject-brief.md"])

    def test_missing_and_orphan(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "reference").mkdir()
            (root / "reference" / "a.md").write_text("a", encoding="utf-8")
            found = check_links(root, "See `reference/a.md` and `reference/b.md`.", ["reference/a.md", "c-brief.md"])
        self.assertEqual(levels(found), [CHECK, NOTE])


class Lines(unittest.TestCase):
    def test_line_rules(self):
        lines = ["Use superpowers:brainstorming.", "Load @reference/a.md now.", "Run python scripts/a.py.",
                 "Run python -I scripts/a.py.", "Mail me at marie@example.md."]
        self.assertEqual(levels(check_lines(lines)), [CHECK, REFUSE, REFUSE])


if __name__ == "__main__":
    unittest.main()
