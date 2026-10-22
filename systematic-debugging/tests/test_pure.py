import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

from polluter import bisect, collect, expand

PYTHON = Path(sys.executable).as_posix()
TOOL = (SCRIPTS / "find_polluter.py").as_posix()
RUNNER = "import runpy, sys\nfor path in sys.argv[1:]:\n    runpy.run_path(path)\n"
POLLUTER = "import os\nos.environ['FIXTURE_MODE'] = 'broken'\nopen('junk.txt', 'w').close()\n"
VICTIM = "import os, sys\nif os.environ.get('FIXTURE_MODE') == 'broken':\n    sys.exit(1)\n"
QUIET = "x = 1\n"
SUITE = {"t/a_test.py": QUIET, "t/b_test.py": POLLUTER, "t/c_test.py": QUIET, "t/d_test.py": VICTIM,
         "runner.py": RUNNER}


def write_tree(root, files):
    for name, text in files.items():
        path = Path(root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class ExpandTest(unittest.TestCase):
    def test_placeholder_takes_every_file(self):
        self.assertEqual(expand("python -m pytest -q {}", ["a.py", "b.py"]),
                         ["python", "-m", "pytest", "-q", "a.py", "b.py"])

    def test_words_after_the_placeholder_stay(self):
        self.assertEqual(expand("npm test -- {} --silent", ["a.ts"]), ["npm", "test", "--", "a.ts", "--silent"])

    def test_quoted_program_path(self):
        self.assertEqual(expand('"C:/Program Files/node/npx.cmd" vitest run {}', ["a.ts"]),
                         ["C:/Program Files/node/npx.cmd", "vitest", "run", "a.ts"])

    def test_no_placeholder(self):
        self.assertIsNone(expand("python -m pytest", ["a.py"]))


class CollectTest(unittest.TestCase):
    def test_any_depth_includes_the_top_folder_and_skips_dependencies(self):
        with tempfile.TemporaryDirectory() as root:
            write_tree(root, {"src/top.test.ts": "", "src/a/b.test.ts": "", "node_modules/x/c.test.ts": "",
                              "src/notes.md": ""})
            self.assertEqual(collect(Path(root), "./src/**/*.test.ts"), ["src/a/b.test.ts", "src/top.test.ts"])


class BisectTest(unittest.TestCase):
    def test_one_polluter_found_wherever_it_sits(self):
        candidates = [f"t{number}.py" for number in range(7)]
        for polluter in candidates:
            self.assertEqual(bisect(candidates, lambda group: polluter in group), ([polluter], True))

    def test_two_files_needed_together(self):
        suspects, single = bisect(["a", "b", "c", "d"], lambda group: {"a", "d"} <= set(group))
        self.assertFalse(single)
        self.assertEqual(suspects, ["a", "b", "c", "d"])


class CommandLineTest(unittest.TestCase):
    def call(self, root, *args):
        command = [PYTHON, "-I", TOOL, "--tests", "t/*_test.py", "--run", f"\"{PYTHON}\" -I runner.py {{}}", *args]
        done = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8")
        return done.returncode, done.stdout

    def test_finds_the_file_that_leaves_junk(self):
        with tempfile.TemporaryDirectory() as root:
            write_tree(root, SUITE)
            code, out = self.call(root, "--creates", "junk.txt")
            self.assertEqual(code, 0, out)
            self.assertIn("polluter: t/b_test.py", out)

    def test_finds_the_file_that_breaks_a_later_test(self):
        with tempfile.TemporaryDirectory() as root:
            write_tree(root, SUITE)
            code, out = self.call(root, "--breaks", "t/d_test.py")
            self.assertEqual(code, 0, out)
            self.assertIn("polluter: t/b_test.py", out)

    def test_refuses_when_the_leftover_is_already_there(self):
        with tempfile.TemporaryDirectory() as root:
            write_tree(root, {**SUITE, "junk.txt": ""})
            code, out = self.call(root, "--creates", "junk.txt")
            self.assertEqual(code, 2)
            self.assertIn("already exists", out)

    def test_refuses_a_victim_that_fails_alone(self):
        with tempfile.TemporaryDirectory() as root:
            write_tree(root, {**SUITE, "t/d_test.py": "raise SystemExit(1)\n"})
            code, out = self.call(root, "--breaks", "t/d_test.py")
            self.assertEqual(code, 2)
            self.assertIn("fails on its own", out)


if __name__ == "__main__":
    unittest.main()
