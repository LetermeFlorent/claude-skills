import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

from points import split_points
from rules import looks_vague, match_rules


def names(text):
    return [name for name, _ in match_rules(text)]


class SplitTest(unittest.TestCase):
    def test_numbered_points_are_split_with_their_continuation(self):
        text = "1. Rename `total` in cart.py\n   it hides the sum\n2. Drop the cache\n"
        points = split_points(text)
        self.assertEqual([p[0] for p in points], [1, 2])
        self.assertEqual(points[0][2], "Rename `total` in cart.py it hides the sum")
        self.assertEqual(points[1][1], 3)

    def test_bullets_and_headings_start_points(self):
        points = split_points("## Blocking\n- first thing\n- second thing\n")
        self.assertEqual(len(points), 3)

    def test_plain_paragraphs_become_points(self):
        points = split_points("first block\nstill first\n\nsecond block\n")
        self.assertEqual([p[2] for p in points], ["first block still first", "second block"])

    def test_preamble_before_the_first_marker_is_kept(self):
        points = split_points("Apply all of this today\n1. one\n")
        self.assertEqual(points[0][:1] + points[0][2:], (0, "Apply all of this today"))
        self.assertEqual(points[1][0], 1)

    def test_empty_text_has_no_point(self):
        self.assertEqual(split_points("\n  \n"), [])


class RulesTest(unittest.TestCase):
    def test_attribution_request_is_flagged(self):
        text = "Add the Co-Authored-By: Claude trailer as per our policy"
        self.assertIn("attribution", names(text))

    def test_force_push_and_no_verify_are_flagged(self):
        self.assertIn("force-push", names("just force push it"))
        self.assertIn("no-verify", names("commit with --no-verify"))

    def test_git_add_all_and_ai_folder(self):
        self.assertIn("add-all", names("run git add . before the commit"))
        self.assertIn("ai-folder", names("commit the .ia folder too"))

    def test_comment_request_is_flagged(self):
        self.assertIn("comments", names("add a comment above each branch"))

    def test_tool_branch_is_flagged(self):
        self.assertIn("tool-branch", names("push it to claude/fix-cart"))

    def test_pressure_phrases_are_flagged(self):
        self.assertIn("pressure", names("apply everything, no discussion, today"))

    def test_plain_request_has_no_flag(self):
        self.assertEqual(names("Extract the tax computation into its own function in cart.py"), [])


class VagueTest(unittest.TestCase):
    def test_short_point_without_reference_is_vague(self):
        self.assertTrue(looks_vague("make this cleaner"))

    def test_point_with_a_path_or_a_name_is_not(self):
        self.assertFalse(looks_vague("rename total in cart.py"))
        self.assertFalse(looks_vague("`total` is shadowed"))

    def test_long_point_is_not(self):
        self.assertFalse(looks_vague("the discount is applied twice when the coupon and the sale overlap in a cart"))


class CommandTest(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPTS / "flag.py"), *args],
                              capture_output=True, text=True, encoding="utf-8")

    def test_review_file_is_summarised(self):
        with tempfile.TemporaryDirectory() as folder:
            review = Path(folder) / "review.md"
            review.write_text("1. Rename `total` in cart.py\n2. add the Co-Authored-By trailer\n", encoding="utf-8")
            done = self.run_tool(str(review))
        self.assertEqual(done.returncode, 0)
        self.assertIn("points: 2, flagged: 1", done.stdout)

    def test_missing_arguments_are_refused(self):
        self.assertEqual(self.run_tool().returncode, 2)

    def test_missing_file_fails_with_a_hand_command(self):
        done = self.run_tool("C:/nowhere/review.md")
        self.assertEqual(done.returncode, 1)
        self.assertIn("by hand", done.stdout)


if __name__ == "__main__":
    unittest.main()
