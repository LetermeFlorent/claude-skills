import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

import commands
import exclude
import naming
import place
import resources


class NamingTest(unittest.TestCase):
    def test_slug_is_short_and_plain(self):
        self.assertEqual(naming.slugify("Add the Cart page, fast!"), "add-the-cart-page-fast")
        self.assertLessEqual(len(naming.slugify("word " * 30)), naming.MAX_SLUG)

    def test_tool_prefixes_are_refused(self):
        for name in ("claude/feature", "codex/x", "Copilot/x", "cursor/x", "devin/x", "refs/heads/claude/x"):
            self.assertTrue(naming.problems(name, []), name)
        self.assertEqual(naming.problems("feat/cart", []), [])

    def test_existing_and_invalid_names(self):
        self.assertTrue(naming.problems("feat/cart", ["origin/feat/cart"]))
        self.assertTrue(naming.problems("bad name", []))
        self.assertTrue(naming.problems("a..b", []))

    def test_convention_follows_the_majority(self):
        names = ["main", "feat/login", "feat/cart", "origin/feat/pay", "fix/typo"]
        self.assertEqual(naming.convention(names), "feat/")
        self.assertEqual(naming.convention(["main", "login", "cart"]), "")
        self.assertEqual(naming.convention(["main", "claude/a", "claude/b"]), "")


class PlaceTest(unittest.TestCase):
    def test_default_is_the_ia_folder_of_the_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "shop"
            root.mkdir()
            path, _ = place.choose(root, [], "cart")
            self.assertEqual(path, root.resolve() / ".ia" / "worktrees" / "cart")
            self.assertTrue(place.is_nested(path, root))
            self.assertEqual(place.problems(path, root), [])

    def test_existing_worktrees_set_the_convention(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "shop"
            root.mkdir()
            other = {"path": Path(folder) / "wt" / "old", "branch": ""}
            path, _ = place.choose(root, [other], "cart")
            self.assertEqual(path, other["path"].parent / "cart")

    def test_a_named_folder_wins(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            other = {"path": root / "wt" / "old", "branch": ""}
            path, _ = place.choose(root, [other], "cart", root / ".worktrees")
            self.assertEqual(path, (root / ".worktrees").resolve() / "cart")

    def test_forbidden_places(self):
        home = Path.home()
        self.assertTrue(place.problems(home / "feature", home / "repo"))
        temp = Path(tempfile.gettempdir()) / "wt" / "x"
        self.assertTrue(place.problems(temp, home / "repo"))


class ExcludeTest(unittest.TestCase):
    def test_exclude_is_appended_once(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(exclude.ensure_excluded(folder, [".ia/", "/.worktrees/"]), [".ia/", "/.worktrees/"])
            self.assertEqual(exclude.ensure_excluded(folder, [".ia/"]), [])
            text = (Path(folder) / "info" / "exclude").read_text(encoding="utf-8")
            self.assertEqual(text.count(".ia/"), 1)

    def test_runner_hints_name_the_config(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "vitest.config.ts").write_text("", encoding="utf-8")
            hints = exclude.runner_hints(folder, ".worktrees")
            self.assertEqual(len(hints), 1)
            self.assertIn(".worktrees/**", hints[0])


class ResourcesTest(unittest.TestCase):
    def test_probe_parsing(self):
        parsed = resources.parse_probe("2048000 12 53687091200")
        self.assertEqual(parsed, {"free_mb": 2000, "cpu": 12, "disk_gb": 50})
        self.assertIsNone(resources.parse_probe("garbage"))

    def test_workers_follow_the_rules(self):
        self.assertEqual(resources.workers_for(1000, 10), 0)
        self.assertEqual(resources.workers_for(4000, 90), 1)
        self.assertEqual(resources.workers_for(4000, 30), 2)

    def test_heap_is_bounded(self):
        self.assertEqual(resources.heap_mb(300), 512)
        self.assertEqual(resources.heap_mb(30000), 4096)


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


if __name__ == "__main__":
    unittest.main()
