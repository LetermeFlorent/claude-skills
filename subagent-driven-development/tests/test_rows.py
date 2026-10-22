import sys
import unittest

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "lib"))

from rows import changed_lines, from_measure, from_scan, proof_lines, split

TAB = chr(9)
BACKSLASH = chr(92)
NEW_FILE = ["diff --git a/pkg/new.py b/pkg/new.py", "new file mode 100644", "index 0000000..1111111",
            "--- /dev/null", "+++ b/pkg/new.py", "@@ -0,0 +1,3 @@", "+a", "+b", "+c"]
MODIFIED = ["diff --git a/x.py b/x.py", "index 1111111..2222222 100644", "--- a/x.py", "+++ b/x.py",
            "@@ -4,0 +5,2 @@", "+x", "+y", "@@ -10 +12 @@", "-old", "+new", "@@ -20,2 +23,0 @@", "-gone", "-gone"]
DELETED = ["diff --git a/gone.py b/gone.py", "deleted file mode 100644", "index 3333333..0000000",
           "--- a/gone.py", "+++ /dev/null", "@@ -1,2 +0,0 @@", "-a", "-b"]


def _row(file, lines, **extra):
    return {"source": "test", "file": file, "lines": lines, "exact": bool(lines), "text": "t", **extra}


class ChangedLinesTest(unittest.TestCase):
    def test_new_modified_and_deleted_files(self):
        found = changed_lines("\n".join(NEW_FILE + MODIFIED + DELETED))
        self.assertEqual(found["pkg/new.py"], {"new": True, "deleted": False, "lines": {1, 2, 3}})
        self.assertEqual(found["x.py"]["lines"], {5, 6, 12})
        self.assertFalse(found["x.py"]["new"])
        self.assertTrue(found["gone.py"]["deleted"])

    def test_paths_with_a_space_or_quoting(self):
        spaced = ["diff --git a/docs/note prix.md b/docs/note prix.md", "--- a/docs/note prix.md" + TAB,
                  "+++ b/docs/note prix.md" + TAB, "@@ -1 +1 @@", "-a", "+b"]
        quoted = ['diff --git "a/a' + BACKSLASH + 'tb.md" "b/a' + BACKSLASH + 'tb.md"',
                  '--- "a/a' + BACKSLASH + 'tb.md"', '+++ "b/a' + BACKSLASH + 'tb.md"', "@@ -2 +2 @@", "-a", "+b"]
        found = changed_lines("\n".join(spaced + quoted))
        self.assertEqual(found["docs/note prix.md"]["lines"], {1})
        self.assertEqual(found["a" + TAB + "b.md"]["lines"], {2})


class ProofTest(unittest.TestCase):
    def test_spans_are_read_only_from_number_lists(self):
        self.assertEqual(proof_lines("numbers 54"), [54])
        self.assertEqual(proof_lines("numbers 38, 53; literal comparisons 85"), [38, 53, 85])
        self.assertEqual(proof_lines("lines 3-5"), [3, 4, 5])
        self.assertEqual(proof_lines("literal comparisons 85; repeated 'a 7' 95, 102"), [85, 95, 102])
        self.assertEqual(proof_lines("params 5 > 4"), [])
        self.assertEqual(proof_lines(None), [])

    def test_measure_rows_on_line_one_are_not_exact(self):
        rows = from_measure([{"file": "a.py", "line": 1, "rule": 3, "what": "never imported", "proof": "no import"},
                             {"file": "a.py", "line": 40, "rule": 6, "what": "params", "proof": "5 > 4"}])
        self.assertEqual([(row["lines"], row["exact"]) for row in rows], [([], False), ([40], True)])

    def test_scan_rows_single_grouped_and_noise(self):
        rows = from_scan("\n".join(["docs/a.md:3 flag: em dash", "docs/a.md flag: delve (lines 2, 4 (+3))",
                                    "scan: 3 files", "docs/b c.md:7 by hand: title case heading"]))
        self.assertEqual([row["file"] for row in rows], ["docs/a.md", "docs/a.md", "docs/b c.md"])
        self.assertEqual(rows[0]["lines"], [3])
        self.assertEqual(rows[1]["lines"], [2, 4])
        self.assertTrue(rows[1]["truncated"])
        self.assertEqual(rows[2]["lines"], [7])


class SplitTest(unittest.TestCase):
    def test_rows_count_only_on_lines_the_task_wrote(self):
        changes = {"a.py": {"new": False, "deleted": False, "lines": {5}},
                   "pkg/new.py": {"new": True, "deleted": False, "lines": {1}}}
        on_line, off_line = _row("a.py", [5]), _row("a.py", [1])
        loose, fresh, folder = _row("a.py", []), _row("pkg/new.py", [9]), _row("pkg", [])
        truncated, elsewhere = _row("a.py", [1], truncated=True), _row("other.py", [5])
        counted, aside = split([on_line, off_line, loose, fresh, folder, truncated, elsewhere], changes)
        self.assertEqual(counted, [on_line, loose, fresh, folder, truncated])
        self.assertEqual(aside, [off_line])

    def test_a_file_without_added_lines_keeps_loose_rows_aside(self):
        changes = {"a.py": {"new": False, "deleted": False, "lines": set()}}
        counted, aside = split([_row("a.py", [])], changes)
        self.assertEqual(counted, [])
        self.assertEqual(len(aside), 1)


if __name__ == "__main__":
    unittest.main()
