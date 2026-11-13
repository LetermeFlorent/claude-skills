import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS / "checks" / "layout"))

import engine
import duplicates
import folders
import junk
import links
import measure
import naming
import runs

SAME = "def money(value):\n    return f\"{value:.2f} EUR\"\n"


def project(base, tree):
    root = Path(base)
    for rel, text in tree.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return [measure.describe(root / rel, root) for rel in tree]


def config(**extra):
    return {**runs.DEFAULTS, **extra}


def rules(findings):
    return sorted((finding["rule"], finding["file"]) for finding in findings)


class EngineTest(unittest.TestCase):
    def test_own_folder_and_every_rule_phased_and_scored(self):
        self.assertEqual(runs.TOOL_PARTS, (".ia", "clean-architecture"))
        self.assertEqual(set(engine.PHASES), set(engine.RULES))
        self.assertEqual(set(engine.EACH) | {0}, set(engine.RULES))


class DuplicatesTest(unittest.TestCase):
    def test_same_content_found_once(self):
        with tempfile.TemporaryDirectory() as base:
            files = project(base, {"a/fmt.py": SAME, "b/fmt.py": SAME + "\n", "a/__init__.py": "", "b/__init__.py": ""})
            found, _ = duplicates.check(files, Path(base), config())
        self.assertEqual(rules(found), [(1, "a/fmt.py")])
        self.assertIn("b/fmt.py", found[0]["what"])


class LinksTest(unittest.TestCase):
    def tree(self, base):
        return project(base, {
            "app/__init__.py": "", "app/ui/__init__.py": "", "app/data/__init__.py": "",
            "app/ui/client.py": "def get():\n    return 1\n",
            "app/ui/view.py": "from app.data.store import load\n\n\ndef show():\n    return load()\n",
            "app/data/store.py": "from app.ui.client import get\n\n\ndef load():\n    return get()\n",
            "main.py": "from app.ui.view import show\n"})

    def test_file_used_from_one_other_folder_is_misplaced(self):
        with tempfile.TemporaryDirectory() as base:
            found, _ = links.check(self.tree(base), Path(base), config())
        misplaced = [f["file"] for f in found if f["rule"] == links.MISPLACED_RULE]
        self.assertIn("app/ui/client.py", misplaced)
        self.assertNotIn("app/ui/view.py", misplaced)

    def test_cycle_between_sibling_folders(self):
        with tempfile.TemporaryDirectory() as base:
            found, _ = links.check(self.tree(base), Path(base), config())
        cycle = [f for f in found if f["rule"] == links.CYCLE_RULE]
        self.assertEqual(len(cycle), 1)
        self.assertIn("app/data/store.py:1", cycle[0]["proof"])
        self.assertTrue(links.related(".", "app/ui"))
        self.assertTrue(links.related("app", "app/ui"))
        self.assertFalse(links.related("app/ui", "app/data"))

    def test_es_imports_without_suffix_and_require(self):
        with tempfile.TemporaryDirectory() as base:
            files = project(base, {
                "src/api/client.js": "export const get = () => 1;\n",
                "src/pages/home.js": "import { get } from '../api/client';\nexport const home = get;\n",
                "src/store/index.js": "const { panel } = require('../views/panel.js');\nmodule.exports = panel;\n",
                "src/views/panel.js": "import start from '../store';\nexport const panel = start;\n"})
            found, _ = links.check(files, Path(base), config())
        self.assertEqual(rules(found), [(2, "src/api/client.js"), (2, "src/store/index.js"),
                                        (2, "src/views/panel.js"), (5, "src/store")])


class FoldersTest(unittest.TestCase):
    def test_empty_folder_chain_and_crowd(self):
        tree = {"pkg/__init__.py": "", "deep/__init__.py": "", "deep/a/__init__.py": "",
                "deep/a/b/__init__.py": "", "deep/a/b/real.py": SAME}
        tree.update({f"many/{group}_{n}.py": SAME + f"N = {n}\n" for group in ("sales", "stock") for n in range(5)})
        with tempfile.TemporaryDirectory() as base:
            found, stats = folders.check(project(base, tree), Path(base), config())
        self.assertIn((3, "pkg"), rules(found))
        self.assertIn((6, "deep"), rules(found))
        crowd = [f for f in found if f["rule"] == folders.CROWDED_RULE]
        self.assertIn("sales/ (5), stock/ (5)", crowd[0]["what"])
        self.assertEqual(stats["code_files"], len(tree))
        self.assertEqual(folders.prefix_groups(["user_a", "user_b", "user_c"], 3), {})


class JunkTest(unittest.TestCase):
    def test_names(self):
        self.assertEqual(junk.junk("debug.log"), "leftover file")
        self.assertEqual(junk.junk("src/cart copy.py"), "copy of another file")
        self.assertEqual(junk.junk("src/photo (1).png"), "copy of another file")
        self.assertIn("__pycache__", junk.junk("src/__pycache__/a.pyc") or "")
        self.assertIsNone(junk.junk("src/copyright.py"))

    def test_tracked_files_are_listed(self):
        with tempfile.TemporaryDirectory() as base:
            files = project(base, {"main.py": SAME, "notes.bak": "x\n", "été.log": "x\n"})
            subprocess.run(["git", "init", "-q"], cwd=base, check=True)
            subprocess.run(["git", "add", "-A"], cwd=base, check=True)
            found, _ = junk.check(files, Path(base), config())
        self.assertEqual(rules(found), [(3, "notes.bak"), (3, "été.log")])

    def test_without_git_the_disk_is_listed(self):
        with tempfile.TemporaryDirectory() as base:
            files = project(base, {"src/main.py": SAME})
            project(base, {"src/notes.bak": "x\n", "debug.log": "x\n"})
            found, _ = junk.check(files, Path(base), config())
        self.assertEqual(rules(found), [(3, "src/notes.bak")])


class NamingTest(unittest.TestCase):
    def test_styles_mixed_names_and_test_places(self):
        self.assertEqual(naming.style("user_card"), "snake_case")
        self.assertEqual(naming.style("userCard"), "camelCase")
        self.assertEqual(naming.style("UserCard"), "PascalCase")
        self.assertIsNone(naming.style("user"))
        tree = {"ui/user_card.py": SAME, "ui/userList.py": SAME, "ui/menu.py": SAME,
                "tests/test_a.py": "import unittest\n", "tests/test_b.py": "import unittest\n",
                "ui/test_c.py": "import unittest\n", "tests/__init__.py": ""}
        with tempfile.TemporaryDirectory() as base:
            found, _ = naming.check(project(base, tree), Path(base), config())
        self.assertEqual(rules(found), [(7, "ui"), (8, "ui/test_c.py")])


if __name__ == "__main__":
    unittest.main()
