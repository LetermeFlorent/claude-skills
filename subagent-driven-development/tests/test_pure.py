import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "lib"))

from ledger import note_problems, parse, pending
from plan import CONSTRAINTS, files_of, is_hard, section, shared, spec, tasks
from repo import porcelain_paths
from space import IGNORED, claimed, ensure_excluded, folder_for, stem

FENCE = "`" * 3
NUL = chr(0)
EM_DASH = chr(0x2014)


class PlanTest(unittest.TestCase):
    def test_tasks_skip_fenced_headings_and_keep_ten_apart_from_one(self):
        lines = ["# Plan", "### Task 1: Add discount", "text", FENCE, "### Task 9: fake", FENCE,
                 "### Task 10: Format price", "end"]
        found = tasks(lines)
        self.assertEqual([task["number"] for task in found], [1, 10])
        self.assertEqual(found[0]["end"], found[1]["start"])
        self.assertEqual(found[1]["end"], len(lines))
        self.assertEqual(found[0]["title"], "Add discount")

    def test_section_stops_at_a_task_heading_but_keeps_subheadings(self):
        lines = ["## Global Constraints", "- no network", "### Detail", "- keep", "### Task 1: Go", "body"]
        self.assertEqual(section(lines, CONSTRAINTS), lines[:4])
        self.assertEqual(section(["## Other"], CONSTRAINTS), [])

    def test_files_drop_line_ranges_and_fenced_lines(self):
        part = ["**Files:**", "- Create: `pricing/discount.py`", "- Modify: `pricing/__init__.py:12-30`",
                "- **Test:** `tests/test_discount.py`", FENCE, "- Create: `fake.py`", FENCE,
                "- Create: `pricing/discount.py`"]
        self.assertEqual(files_of(part), ["pricing/discount.py", "pricing/__init__.py", "tests/test_discount.py"])

    def test_hard_comes_from_the_title_or_a_difficulty_line(self):
        self.assertTrue(is_hard({"title": "Parser (hard)"}, []))
        self.assertTrue(is_hard({"title": "Parser"}, ["**Difficulty:** hard"]))
        self.assertFalse(is_hard({"title": "Parser"}, [FENCE, "Difficulty: hard", FENCE]))
        self.assertFalse(is_hard({"title": "Hardware probe"}, ["Difficulty: easy"]))

    def test_shared_lists_each_pair_with_common_paths(self):
        self.assertEqual(shared({1: ["a", "b"], 2: ["b"], 3: ["c"]}), [(1, 2, ["b"])])

    def test_spec_reads_the_first_spec_line(self):
        self.assertEqual(spec(["# Plan", "**Spec:** `docs/spec.md`"]), "docs/spec.md")
        self.assertIsNone(spec(["# Plan"]))


class LedgerTest(unittest.TestCase):
    def test_parse_reads_completions_rounds_rulings_and_final(self):
        state = parse(["# SDD ledger, plan: p.md", "Task 1: complete, commit abc1234, review clean",
                       "Task 3,4: complete, commit 1234567, review clean", "Task 2: fix round 2/4, two findings",
                       "Ruling: keep cents | why: spec | if wrong: one test", "Final: complete"])
        self.assertEqual(state["complete"], {1: "abc1234", 3: "1234567", 4: "1234567"})
        self.assertEqual(state["rounds"], {2: 2})
        self.assertEqual(len(state["rulings"]), 1)
        self.assertTrue(state["final"])
        self.assertEqual(pending([1, 2, 3, 4, 5], state), [2, 5])

    def test_notes_refuse_dashes_new_lines_and_unknown_prefixes(self):
        self.assertEqual(note_problems("Note: plain line"), [])
        self.assertEqual(len(note_problems(f"Note: a {EM_DASH} b")), 1)
        self.assertEqual(note_problems("Note: a" + chr(10) + "b"), ["one line per note"])
        self.assertEqual(len(note_problems("random text")), 1)


class SpaceTest(unittest.TestCase):
    def test_folder_is_keyed_by_project_and_plan(self):
        folder = folder_for(Path("base"), "shop", Path("C:/repo/.ia/plans/2026 prix.md"))
        self.assertEqual(folder.parent.name, "shop-sdd")
        self.assertRegex(folder.name, r"^2026-prix-[0-9a-f]{6}$")
        other = folder_for(Path("base"), "shop", Path("C:/other/.ia/plans/2026 prix.md"))
        self.assertNotEqual(folder, other)

    def test_stem_accepts_numbers_and_final_only(self):
        self.assertEqual(stem("1,2"), "task-1+2")
        self.assertEqual(stem("final"), "task-final")
        with self.assertRaises(ValueError):
            stem("../x")

    def test_claimed_refuses_folders_tooling_and_outside_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            (root / "sub").mkdir()
            (root / "a.txt").write_text("a", encoding="utf-8")
            paths, problems = claimed(root, ["a.txt", "sub", ".ia/plans/p.md", "../outside.txt", "a.txt"])
        self.assertEqual(paths, ["a.txt"])
        self.assertEqual(len(problems), 3)

    def test_exclude_line_is_added_once(self):
        with tempfile.TemporaryDirectory() as raw:
            exclude = Path(raw) / "info" / "exclude"
            self.assertTrue(ensure_excluded(exclude))
            self.assertFalse(ensure_excluded(exclude))
            self.assertEqual(exclude.read_text(encoding="utf-8").split(), [IGNORED])


class RepoTest(unittest.TestCase):
    def test_porcelain_keeps_both_sides_of_a_rename(self):
        output = NUL.join([" M a.py", "?? new dir/b.txt", "R  new.py", "old.py", ""])
        self.assertEqual(porcelain_paths(output), {"a.py", "new dir/b.txt", "new.py", "old.py"})


if __name__ == "__main__":
    unittest.main()
