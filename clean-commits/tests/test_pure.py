import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

import repo
from checks import _mentions
from commit import _relative
from common import QUIET_ENV
from message import ATTRIBUTION
from push import ACCOUNTS_VAR, _accounts_problems, _command
from repo import FIELD, GIT, GITHUB_KIND, RECORD

ROOT = Path(tempfile.gettempdir()) / "work"
TARGET = {"kind": GITHUB_KIND, "owner": "someone", "url": "https://github.com/someone/repo.git"}
MISSING = Path(tempfile.gettempdir()) / "claude-skills-no-such-tool"


class PushCommandTest(unittest.TestCase):
    def test_git_never_opens_a_credential_window(self):
        self.assertEqual(QUIET_ENV["GIT_TERMINAL_PROMPT"], "0")
        self.assertEqual(QUIET_ENV["GCM_INTERACTIVE"], "never")

    def test_plain_push_without_the_account_tool(self):
        self.assertEqual(_command(ROOT, TARGET, ["push"], MISSING), [GIT, "push"])

    def test_plain_push_when_the_variable_is_unset_or_empty(self):
        for value in (None, ""):
            with mock.patch.dict(os.environ):
                os.environ.pop(ACCOUNTS_VAR, None)
                if value is not None:
                    os.environ[ACCOUNTS_VAR] = value
                self.assertEqual(_command(ROOT, TARGET, ["push"]), [GIT, "push"])

    def test_account_tool_named_by_the_variable(self):
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            tool = Path(handle.name)
        self.addCleanup(tool.unlink)
        with mock.patch.dict(os.environ, {ACCOUNTS_VAR: str(tool)}):
            command = _command(ROOT, TARGET, ["push"])
        self.assertEqual(command[1], str(tool))

    def test_account_tool_when_installed(self):
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            tool = Path(handle.name)
        self.addCleanup(tool.unlink)
        command = _command(ROOT, TARGET, ["push"], tool)
        self.assertEqual(command[1:4], [str(tool), "run", "github"])
        self.assertIn("someone", command)
        self.assertEqual(command[-1], "push")

    def test_missing_account_tool_is_refused_not_ignored(self):
        self.assertTrue(_accounts_problems(TARGET, MISSING))
        self.assertEqual(_accounts_problems(TARGET, None), [])
        self.assertEqual(_accounts_problems({**TARGET, "kind": "plain"}, MISSING), [])

    def test_variable_with_a_tilde_is_expanded(self):
        with tempfile.TemporaryDirectory() as home:
            tool = Path(home) / "comptes"
            tool.write_text("", encoding="utf-8")
            with mock.patch.dict(os.environ, {ACCOUNTS_VAR: "~/comptes", "HOME": home, "USERPROFILE": home}):
                self.assertEqual(Path(_command(ROOT, TARGET, ["push"])[1]), tool)


class RepoTest(unittest.TestCase):
    def test_renames_keep_both_names(self):
        with mock.patch.object(repo, "read", return_value="R  new.ts\0old.ts\0?? added.ts\0"):
            entries = repo.changes(ROOT)
        self.assertEqual((entries[0]["path"], entries[0]["from"]), ("new.ts", "old.ts"))
        self.assertTrue(entries[1]["new"])

    def test_unpushed_attribution_is_read_in_one_git_call(self):
        log = f"abc1234{FIELD}fix\n\nClaude-Session: x{RECORD}\ndef5678{FIELD}claude-skills: ok{RECORD}\n"
        with mock.patch.object(repo, "read", return_value="HEAD"):
            with mock.patch.object(repo, "git", return_value=(0, log, "")) as git:
                self.assertEqual(repo.unpushed_matching(ROOT, ATTRIBUTION), ["abc1234"])
        self.assertEqual(git.call_count, 1)

    def test_a_failing_git_log_is_an_error_not_a_clean_history(self):
        with mock.patch.object(repo, "read", return_value="HEAD"):
            with mock.patch.object(repo, "git", return_value=(None, "", "git timed out after 60 s")):
                self.assertRaises(RuntimeError, repo.unpushed_matching, ROOT, ATTRIBUTION)
                self.assertRaises(RuntimeError, repo.unpushed, ROOT)

    def test_no_commit_yet_means_nothing_unpushed(self):
        with mock.patch.object(repo, "read", return_value=None):
            self.assertEqual(repo.unpushed(ROOT), [])
            self.assertEqual(repo.unpushed_matching(ROOT, ATTRIBUTION), [])


class ChecksTest(unittest.TestCase):
    def test_a_short_name_does_not_match_a_longer_path(self):
        self.assertEqual(_mentions("src/data.ts:3:1 error", ROOT, ["a.ts"]), [])
        self.assertEqual(_mentions("src/a.ts:3:1 error", ROOT, ["a.ts"]), [])
        self.assertEqual(len(_mentions("a.ts:3:1 error\n./a.ts(2,1): x", ROOT, ["a.ts"])), 2)

    def test_absolute_and_package_relative_paths_match(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "packages" / "app").mkdir(parents=True)
            (root / "packages" / "app" / "package.json").write_text("{}", encoding="utf-8")
            output = f"{root / 'b.ts'}\n  1:1 error\nsrc/x.ts(1,1): error"
            self.assertEqual(len(_mentions(output, root, ["b.ts", "packages/app/src/x.ts"])), 2)


class CommitTest(unittest.TestCase):
    def test_a_path_outside_the_repository_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve() / "repo"
            self.assertIsNone(_relative(root, str(Path(folder) / "elsewhere.txt")))
            self.assertEqual(_relative(root, str(root / "src" / "a.ts")), "src/a.ts")
            self.assertEqual(_relative(root, "src\\a.ts"), "src/a.ts")


if __name__ == "__main__":
    unittest.main()
