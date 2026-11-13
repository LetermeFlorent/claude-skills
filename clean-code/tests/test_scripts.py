import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / "lib"), str(SCRIPTS / "checks" / "project")]

import files
import plan_check
import repository
import runs
import score
import store

TRAILER = "Co-Authored-By: Claude <noreply@" + "anthropic.com>"

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false"]
PLAN = """<!-- clean-code plan v1 -->
# Plan clean-code

Scope: src
Run: 2026-01-01-000000, note 19/20
{suite}
## Step 1: Serve hero.png through a `<picture>` element typed as `Promise<void>`

Phase: 3
Findings: M1
Safe: no
Files: src/hero.tsx
Check: pnpm test
Commit: Serve the hero image as WebP

## Left as is

none
"""
FINDINGS = {"M1": {"id": "M1", "rule": 19, "status": "confirmed"}}


def git(root, *args):
    subprocess.run([*GIT, "-C", str(root), *args], check=True, capture_output=True)


def commit(root, message):
    git(root, "commit", "--no-verify", "--allow-empty", "-q", "-m", message)


class ScoreTest(unittest.TestCase):
    def test_any_deduction_keeps_the_note_under_twenty(self):
        self.assertEqual(score._rounded(score.TOP - 0.25), 19.5)
        self.assertEqual(score._rounded(score.TOP - 0.01), 19.5)
        taken = score.deductions([{"rule": 14, "file": "a.py"}], {"comment_scanned": 1000})
        self.assertEqual(score._rounded(score.TOP - sum(taken.values())), 19.5)

    def test_exact_steps_stay(self):
        self.assertEqual(score._rounded(score.TOP), 20)
        self.assertEqual(score._rounded(score.TOP - 1.5), 18.5)

    def test_one_comment_finding_is_a_small_share(self):
        self.assertEqual(score.deductions([{"rule": 14, "file": "a.py"}], {"comment_scanned": 200}), {14: 0.01})


class PlanCheckTest(unittest.TestCase):
    def test_code_spans_are_no_placeholders(self):
        text = PLAN.format(suite="Suite: pnpm test, green at the start: yes\n")
        self.assertEqual(plan_check.check(text, FINDINGS)[0], [])

    def test_missing_suite_line_refused(self):
        self.assertIn("the Suite: line is missing", plan_check.check(PLAN.format(suite=""), FINDINGS)[0])

    def test_bare_placeholder_refused(self):
        text = PLAN.format(suite="Suite: <command>\n")
        self.assertIn("template placeholder left: <command>", plan_check.check(text, FINDINGS)[0])


class StoreTest(unittest.TestCase):
    def test_orphan_lock_is_taken_within_one_wait(self):
        self.assertLess(store.LOCK_STALE, store.LOCK_WAIT)
        with tempfile.TemporaryDirectory() as base:
            lock = Path(base, store.LOCK)
            lock.write_text("", encoding="utf-8")
            old = time.time() - store.LOCK_STALE - 1
            os.utime(lock, (old, old))
            store._acquire(lock)
            self.assertTrue(lock.exists())


class GitCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name, "main")
        self.root.mkdir()
        git(self.root, "init", "-q")

    def tearDown(self):
        self.temp.cleanup()

    def test_worktree_ignores_the_tool_folder(self):
        commit(self.root, "start")
        side = Path(self.temp.name, "side")
        git(self.root, "worktree", "add", "-q", str(side))
        (runs.tool_dir(side) / "run.json").write_text("{}", encoding="utf-8")
        status = subprocess.run(["git", "-C", str(side), "status", "--short"], capture_output=True, text=True)
        self.assertNotIn(".ia", status.stdout)

    def test_walk_follows_gitignore(self):
        for rel, text in {".gitignore": "gen/\n", "a.py": "", "b.py": "", "gen/x.py": ""}.items():
            (self.root / rel).parent.mkdir(exist_ok=True)
            (self.root / rel).write_text(text, encoding="utf-8")
        git(self.root, "add", "a.py")
        listed = [files.relative(path, self.root) for path in files.walk(self.root, self.root, runs.DEFAULTS)]
        self.assertEqual(listed, [".gitignore", "a.py", "b.py"])

    def test_pushed_attribution_counted_in_one_listing(self):
        commit(self.root, "Fix\n\n" + TRAILER)
        git(self.root, "update-ref", "refs/remotes/origin/main", "HEAD")
        commit(self.root, "Tidy\n\n" + TRAILER)
        found = repository._history(self.root)[0]
        self.assertTrue(found["what"].startswith("2 commits"))
        self.assertTrue(found["proof"].startswith("1 already pushed: "))


if __name__ == "__main__":
    unittest.main()
