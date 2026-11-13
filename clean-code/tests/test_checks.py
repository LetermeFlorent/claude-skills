import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / "lib"), str(SCRIPTS / "checks" / "files"),
                str(SCRIPTS / "checks" / "project")]

import deadcode
import functions
import hardcoded
import images
import measure
import runs

TOKEN = "ghp_" + "a" * 36


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def describe(self, tree):
        for rel, text in tree.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(text, bytes):
                path.write_bytes(text)
            else:
                path.write_text(text, encoding="utf-8")
        return {rel: measure.describe(self.root / rel, self.root) for rel in tree}


class HardcodedTest(ProjectCase):
    def test_repeated_secret_is_masked(self):
        line = f'headers = {{"Authorization": "Bearer {TOKEN}"}}\n'
        item = self.describe({"s.py": f"def a():\n    {line}\ndef b():\n    {line}"})["s.py"]
        found, _ = hardcoded.check([item], self.root, dict(runs.DEFAULTS))
        self.assertTrue(found)
        self.assertNotIn(TOKEN, found[0]["proof"])
        self.assertIn("chars)", found[0]["proof"])

    def test_repeated_plain_text_is_quoted(self):
        item = self.describe({"s.py": 'def a():\n    g("next page")\n\ndef b():\n    g("next page")\n'})["s.py"]
        found, _ = hardcoded.check([item], self.root, dict(runs.DEFAULTS))
        self.assertIn("'next page'", found[0]["proof"])


class DeadcodeTest(ProjectCase):
    def test_test_classes_are_not_unused_symbols(self):
        items = self.describe({"tests/test_foo.py": "import unittest\n\n\nclass FooTest(unittest.TestCase):\n"
                                                    "    def test_one(self):\n        self.assertTrue(True)\n"})
        found, _ = deadcode.check(list(items.values()), self.root, dict(runs.DEFAULTS))
        self.assertFalse([finding for finding in found if "used nowhere" in finding["what"]])

    def test_import_from_outside_the_scope_counts(self):
        items = self.describe({"a/mod.py": "def helper():\n    return 2\n",
                               "b/use.py": "from a.mod import helper\n\nprint(helper())\n"})
        config = {**runs.DEFAULTS, "project_files": list(items.values())}
        found, _ = deadcode.check([items["a/mod.py"]], self.root, config)
        self.assertEqual(found, [])

    def test_image_used_outside_the_scope_is_referenced(self):
        items = self.describe({"a/logo.webp": b"RIFF0000WEBPVP8 " + bytes(30),
                               "b/page.html": '<p><img src="../a/logo.webp"></p>\n'})
        config = {**runs.DEFAULTS, "project_files": list(items.values())}
        found, _ = images.check([items["a/logo.webp"]], self.root, config)
        self.assertFalse([finding for finding in found if finding["rule"] == images.DEAD_RULE])


class FunctionsTest(unittest.TestCase):
    def test_call_before_a_block_is_no_function_without_semicolons(self):
        codes = ["func main() {", "    fmt.Println(x)", "    if err != nil {", "        return", "    }", "}"]
        self.assertEqual([found[0] for found in functions._braced(codes, False)], ["main"])

    def test_brace_on_next_line_still_found_with_semicolons(self):
        codes = ["int main()", "{", "    return 0;", "}"]
        self.assertEqual([found[0] for found in functions._braced(codes, True)], ["main"])


if __name__ == "__main__":
    unittest.main()
