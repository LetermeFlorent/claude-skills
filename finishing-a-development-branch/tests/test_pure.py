import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

import verdict


class EnvironmentTest(unittest.TestCase):
    def test_same_directories_mean_a_normal_repository(self):
        self.assertEqual(verdict.environment("/r/.git", "/r/.git", "feature"), "normal")

    def test_a_worktree_on_a_branch(self):
        self.assertEqual(verdict.environment("/r/.git/worktrees/x", "/r/.git", "feature"), "worktree")

    def test_a_worktree_without_branch_is_detached(self):
        self.assertEqual(verdict.environment("/r/.git/worktrees/x", "/r/.git", ""), "detached")


class BaseTest(unittest.TestCase):
    def test_fewest_commits_ahead_wins(self):
        self.assertEqual(verdict.pick_base({"main": 3, "release": 9}), ("main", False))

    def test_a_preferred_name_breaks_a_tie(self):
        self.assertEqual(verdict.pick_base({"main": 3, "topic": 3}), ("main", False))

    def test_two_unknown_names_tied_are_ambiguous(self):
        self.assertEqual(verdict.pick_base({"alpha": 2, "beta": 2}), ("alpha", True))

    def test_main_and_master_tied_are_ambiguous(self):
        self.assertEqual(verdict.pick_base({"main": 2, "master": 2}), ("main", True))

    def test_no_candidate(self):
        self.assertEqual(verdict.pick_base({}), (None, False))


class AttributionTest(unittest.TestCase):
    def test_tool_trailers(self):
        host, tool, cursor = "anthropic", "Claude", "Cur" + "sor"
        texts = (f"fix\n\nCo-Authored-By: {tool} <noreply@{host}.com>", "x\nGenerated" + " with " + tool,
                 f"x\n{tool}-Session: 1", f"x\nMade-with: {cursor}", f"x\nSee https://{tool.lower()}.ai/code/abc")
        for text in texts:
            self.assertTrue(verdict.has_attribution(text), text)

    def test_plain_messages_pass(self):
        self.assertFalse(verdict.has_attribution("Ajoute le panier\n\nCo-authored-by: Lea Martin <lea@example.org>"))


class WorktreeTest(unittest.TestCase):
    def test_owned_folders(self):
        self.assertTrue(verdict.owned_worktree("/r/.worktrees/a", "/r"))
        self.assertTrue(verdict.owned_worktree("/r/worktrees/a", "/r"))
        self.assertTrue(verdict.owned_worktree("/r/.ia/worktrees/a", "/r"))

    def test_foreign_paths(self):
        self.assertFalse(verdict.owned_worktree("/elsewhere/a", "/r"))
        self.assertFalse(verdict.owned_worktree("/r/src/a", "/r"))
        self.assertFalse(verdict.owned_worktree("/r", "/r"))
        self.assertFalse(verdict.owned_worktree("/r/.ia/notes", "/r"))
        self.assertFalse(verdict.owned_worktree("/r/.ia/worktrees", "/r"))

    def test_removal_needs_landed_clean_and_owned(self):
        self.assertFalse(verdict.removal(False, True, 0, 0)[0])
        self.assertFalse(verdict.removal(True, False, 0, 0)[0])
        self.assertFalse(verdict.removal(True, True, 2, 0)[0])
        self.assertTrue(verdict.removal(True, True, 0, 0)[0])

    def test_removal_warns_about_ia_files(self):
        self.assertIn("3 files", verdict.removal(True, True, 0, 3)[1])


class ProjectTest(unittest.TestCase):
    def test_test_hints_are_unique(self):
        self.assertEqual(verdict.test_hints({"pyproject.toml", "pytest.ini", "README.md"}), ["python -m pytest"])

    def test_python_test_files_give_a_hint(self):
        self.assertEqual(verdict.test_hints({"test_calc.py"}), ["python -m unittest discover"])

    def test_no_hint(self):
        self.assertEqual(verdict.test_hints({"README.md"}), [])

    def test_template_lookup_ignores_case(self):
        self.assertEqual(verdict.find_template({".github/PULL_REQUEST_TEMPLATE.md", "a.py"}),
                         ".github/PULL_REQUEST_TEMPLATE.md")
        self.assertIsNone(verdict.find_template({"a.py"}))


if __name__ == "__main__":
    unittest.main()
