import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RUN = HERE.parent / "scripts" / "run.py"
sys.path.insert(0, str(HERE.parent / "scripts" / "lib"))

from commands import build
from detect import find_root, node_tool, runners

SOURCE = "def area(width, height):\n    return 0\n"
TESTS = ("import unittest\n\nfrom geometry import area\n\n\nclass AreaTest(unittest.TestCase):\n"
         "    def test_area_square(self):\n        self.assertEqual(area(2, 2), 4)\n\n"
         "    def test_area_flat(self):\n        self.assertEqual(area(3, 0), 0)\n")
RED_ID = "tests/test_geometry.py::AreaTest::test_area_square"
PASSING_ID = "tests/test_geometry.py::AreaTest::test_area_flat"
RUN_TIMEOUT = 120


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class DetectTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="tdd-detect-")
        self.root = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def test_plain_python_is_unittest(self):
        write(self.root, "tests/test_geometry.py", TESTS)
        self.assertEqual(runners(self.root, None), ["unittest"])

    def test_pytest_is_seen_from_config_or_imports(self):
        write(self.root, "tests/test_geometry.py", "import pytest\n")
        self.assertEqual(runners(self.root, None), ["pytest"])
        write(self.root, "pyproject.toml", "[tool.pytest.ini_options]\naddopts = \"-n auto\"\n")
        command, _ = build("pytest", self.root, None, 2)
        self.assertEqual(command[-2:], ["-n", "2"])

    def test_node_runner_from_test_script_and_target_suffix(self):
        write(self.root, "package.json", json.dumps({"scripts": {"test": "vitest"}}))
        write(self.root, "tools/test_build.py", "")
        write(self.root, "requirements.txt", "")
        self.assertEqual(runners(self.root, "src/tax.test.ts"), ["vitest", "unittest"])
        self.assertEqual(runners(self.root, "tools/test_build.py")[0], "unittest")
        with self.assertRaises(LookupError):
            build("vitest", self.root, None, 2)

    def test_local_binary_is_used(self):
        write(self.root, "package.json", json.dumps({"devDependencies": {"jest": "30"}}))
        suffix = ".cmd" if sys.platform == "win32" else ""
        write(self.root, f"node_modules/.bin/jest{suffix}", "")
        command, _ = build("jest", self.root, "src/tax.test.js::adds tax", 2)
        self.assertEqual(command[0], node_tool(self.root, "jest"))
        self.assertEqual(command[1:], ["--watchAll=false", "--maxWorkers=2", "src/tax.test.js", "-t", "adds tax"])

    def test_root_is_the_nearest_marker(self):
        write(self.root, "web/package.json", "{}")
        self.assertEqual(find_root(self.root / "web" / "src"), self.root / "web")


class RunTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="tdd-run-")
        self.root = Path(self.folder.name)
        write(self.root, "geometry.py", SOURCE)
        write(self.root, "tests/test_geometry.py", TESTS)

    def tearDown(self):
        self.folder.cleanup()

    def run_script(self, *arguments):
        done = subprocess.run([sys.executable, "-I", str(RUN), *arguments], cwd=self.root, capture_output=True,
                              text=True, encoding="utf-8", timeout=RUN_TIMEOUT)
        return done.returncode, done.stdout

    def test_red_is_accepted_on_a_failed_assertion(self):
        code, out = self.run_script("--expect", "red", RED_ID)
        self.assertEqual(code, 0, out)
        self.assertIn("AssertionError: 0 != 4", out)

    def test_red_is_refused_when_the_test_passes_or_nothing_ran(self):
        self.assertEqual(self.run_script("--expect", "red", PASSING_ID)[0], 2)
        code, out = self.run_script("--expect", "red", "tests/test_geometry.py::AreaTest::test_area_typo")
        self.assertEqual(code, 2)
        self.assertIn("no test ran", out)

    def test_green_suite_after_the_fix(self):
        write(self.root, "geometry.py", "def area(width, height):\n    return width * height\n")
        code, out = self.run_script("--expect", "green", "--suite")
        self.assertEqual(code, 0, out)
        self.assertIn("green: 2 passed", out)
        self.assertFalse(list(self.root.rglob("__pycache__")))
