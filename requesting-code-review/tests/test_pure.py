import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts" / "lib"))

import attribution
import gitrange

RANGE = SKILL / "scripts" / "range.py"
NO_HOOKS = tempfile.mkdtemp(prefix="hooks-")


def tearDownModule():
    shutil.rmtree(NO_HOOKS, ignore_errors=True)


def commit(repo, name, text, message):
    (Path(repo) / name).write_text(text, encoding="utf-8")
    run(repo, "add", name)
    run(repo, "-c", f"core.hooksPath={NO_HOOKS}", "commit", "-q", "-m", message)


def run(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def make_repo(folder):
    run(folder, "init", "-q", "-b", "main")
    run(folder, "config", "user.name", "Test Person")
    run(folder, "config", "user.email", "test@example.org")
    commit(folder, "a.txt", "one\n", "first")
    return folder


class AttributionTest(unittest.TestCase):
    def test_trailers_are_found(self):
        text = "fix\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nMade-with: Cursor"
        self.assertEqual(len(attribution.message_hits(text)), 2)

    def test_human_co_author_stays(self):
        self.assertEqual(attribution.message_hits("fix\n\nCo-authored-by: Claude Martin <claude@example.org>"), [])

    def test_bot_author_is_found(self):
        self.assertTrue(attribution.author_hit("copilot-swe-agent[bot]"))
        self.assertFalse(attribution.author_hit("Marie"))

    def test_branch_prefix(self):
        self.assertTrue(attribution.branch_hit("claude/fix-1"))
        self.assertFalse(attribution.branch_hit("fix/claude-md"))

    def test_findings_name_the_commit(self):
        row = {"sha": "abcdef012345", "author": "Dev", "committer": "x (aider)", "body": "msg"}
        self.assertEqual(attribution.findings([row]), ["abcdef0 committer: x (aider)"])


class RangeTest(unittest.TestCase):
    def setUp(self):
        self.holder = tempfile.TemporaryDirectory(prefix="range-")
        self.repo = make_repo(self.holder.name)

    def tearDown(self):
        self.holder.cleanup()

    def call(self, *args):
        return subprocess.run([sys.executable, "-I", str(RANGE), "--repo", self.repo, *args],
                              capture_output=True, text=True, encoding="utf-8")

    def test_lists_commits_and_files(self):
        commit(self.repo, "b.txt", "two\n", "add b")
        done = self.call()
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("A b.txt", done.stdout)
        self.assertIn("attribution: none", done.stdout)

    def test_reports_attribution(self):
        commit(self.repo, "b.txt", "two\n", "add b\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
        self.assertIn("attribution: 1", self.call().stdout)

    def test_refuses_empty_range(self):
        head = gitrange.resolve(self.repo, "HEAD")
        done = self.call("--base", head)
        self.assertEqual(done.returncode, 2)

    def test_refuses_unknown_base(self):
        self.assertEqual(self.call("--base", "nope").returncode, 2)

    def test_refuses_outside_a_repository(self):
        with tempfile.TemporaryDirectory(prefix="norepo-") as folder:
            done = subprocess.run([sys.executable, "-I", str(RANGE), "--repo", folder],
                                  capture_output=True, text=True)
            self.assertEqual(done.returncode, 2)

    def test_base_from_branch_point(self):
        run(self.repo, "checkout", "-q", "-b", "feature")
        commit(self.repo, "b.txt", "two\n", "add b")
        commit(self.repo, "c.txt", "three\n", "add c")
        done = self.call()
        self.assertIn("merge-base with main", done.stdout)
        self.assertIn("commits: 2", done.stdout)


if __name__ == "__main__":
    unittest.main()
