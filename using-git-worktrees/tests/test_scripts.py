import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

import baseline
import commands
import state


class CommandsTest(unittest.TestCase):
    def make(self, files):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        for name, text in files.items():
            path = Path(folder.name) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return folder.name

    def test_node_runner_gets_two_workers(self):
        root = self.make({"package.json": '{"scripts": {"test": "vitest run"}}'})
        self.assertEqual(commands.test_command(root, 2), ["npm", "test", "--", "--maxWorkers=2"])

    def test_plain_node_test_has_no_flag(self):
        root = self.make({"package.json": '{"scripts": {"test": "node --test"}}'})
        self.assertEqual(commands.test_command(root, 2), ["npm", "test"])

    def test_cargo_and_go(self):
        self.assertIn("-j", commands.test_command(self.make({"Cargo.toml": ""}), 1))
        self.assertEqual(commands.test_command(self.make({"go.mod": ""}), 2)[:3], ["go", "test", "-p"])

    def test_python_without_pytest_uses_unittest(self):
        root = self.make({"tests/test_a.py": ""})
        self.assertEqual(commands.test_command(root, 2), ["python", "-m", "unittest", "discover", "-s", "tests"])

    def test_python_declaring_pytest_uses_it(self):
        self.assertEqual(commands.test_command(self.make({"pytest.ini": ""}), 2), ["python", "-m", "pytest", "-q"])
        root = self.make({"pyproject.toml": "[tool.pytest.ini_options]\n", "tests/test_a.py": ""})
        self.assertEqual(commands.test_command(root, 2)[2], "pytest")

    def test_install_only_when_missing(self):
        root = self.make({"package.json": "{}", "package-lock.json": "{}"})
        self.assertEqual(commands.install_command(root)[:2], ["npm", "ci"])
        (Path(root) / "node_modules").mkdir()
        self.assertIsNone(commands.install_command(root))

    def test_list_mode_never_runs_the_suite(self):
        root = self.make({"package.json": '{"scripts": {"test": "vitest run"}}', "node_modules/.bin/vitest": ""})
        self.assertEqual(commands.list_command(root)[1:], ["list"])
        self.assertIsNone(commands.list_command(self.make({"package.json": '{"scripts": {"test": "vitest"}}'})))
        self.assertIn("--collect-only", commands.list_command(self.make({"pytest.ini": ""})))
        self.assertIsNone(commands.list_command(self.make({"tests/test_a.py": ""})))

    def test_worktree_seen_in_runner_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            worktree = root / ".ia" / "worktrees" / "cart"
            self.assertTrue(commands.reads_worktree(" .ia\\worktrees\\cart/src/a.test.ts", worktree, root))
            self.assertTrue(commands.reads_worktree(f"{worktree}/x.py::t", worktree, root))
            self.assertFalse(commands.reads_worktree("src/a.test.ts\n.ia/worktrees/cartography/x", worktree, root))


class BaselineTest(unittest.TestCase):
    def test_install_failure_and_timeout_are_not_red_tests(self):
        self.assertEqual(baseline.status(0, baseline.TESTS), "BASELINE DONE exit=0")
        self.assertEqual(baseline.status(1, baseline.TESTS), "BASELINE FAILED exit=1")
        self.assertEqual(baseline.status(1, baseline.INSTALL), "BASELINE INSTALL FAILED exit=1")
        self.assertTrue(baseline.status(None, baseline.TESTS).startswith("BASELINE TIMED OUT after 540 s"))

    def test_failing_list_command_is_not_reported_safe(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            listing = mock.patch.object(baseline.commands, "list_command", return_value=["python", "-m", "pytest"])
            failing = mock.patch.object(baseline, "run", return_value=(1, "", "No module named pytest"))
            with listing, failing:
                result = baseline.runner_check(root, root / ".ia" / "worktrees" / "cart")
        self.assertIn("check the runner hints by hand", result)


class FetchTest(unittest.TestCase):
    def test_no_bare_fetch_without_the_accounts_tool(self):
        for value in (None, "", str(Path(tempfile.gettempdir()) / "claude-skills-no-such-tool")):
            lines = state.fetch_lines(Path("/repo"), "someone", value)
            self.assertIn("ask the user", lines[0])
            self.assertNotIn("fetch origin", "\n".join(lines))

    def test_fetch_goes_through_the_accounts_tool(self):
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            tool = Path(handle.name)
        self.addCleanup(tool.unlink)
        line = state.fetch_lines(Path("/repo"), "someone", str(tool))[1]
        self.assertIn(f'sh "{tool.as_posix()}" run github someone', line)
        self.assertIn("password=\\$GH_TOKEN", line)
        self.assertTrue(line.endswith("fetch origin"))


@unittest.skipUnless(shutil.which("git"), "git is not installed")
class CreateTest(unittest.TestCase):
    def test_relative_path_from_a_subfolder_is_where_git_puts_it(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve() / "shop"
            (root / "sub").mkdir(parents=True)
            env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
            for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "init"]):
                subprocess.run(["git", *args], cwd=root, env=env, check=True, capture_output=True)
            done = subprocess.run([sys.executable, "-I", str(SCRIPTS / "create.py"), "--branch", "cart", "--path",
                                   "../.ia/worktrees/cart"], cwd=root / "sub", env=env, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertTrue((root / ".ia" / "worktrees" / "cart" / ".git").exists())
            self.assertIn(f"worktree: {(root / '.ia' / 'worktrees' / 'cart').as_posix()}", done.stdout)


if __name__ == "__main__":
    unittest.main()
