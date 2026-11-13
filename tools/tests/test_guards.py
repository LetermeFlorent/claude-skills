import subprocess
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
INTERRUPTED = 130
PROBE = """
import inspect, sys
sys.path.insert(0, sys.argv[1])
import common
def main():
    print("\\u2192 \\u00e9t\\u00e9")
    raise {error}("boom")
args = ("probe", main, "run it again") if len(inspect.signature(common.guard).parameters) == 3 else (main, "run it again")
common.guard(*args)
"""


def guards():
    return sorted(path for path in REPO.glob("*/scripts/**/common.py") if "def guard(" in path.read_text("utf-8"))


def probe(path, error):
    return subprocess.run([sys.executable, "-I", "-B", "-c", PROBE.format(error=error), str(path.parent)],
                          capture_output=True, env={"PYTHONIOENCODING": "cp1252", "SYSTEMROOT": "C:\\Windows"})


class GuardsTest(unittest.TestCase):
    def test_every_skill_guard_behaves_the_same(self):
        self.assertGreaterEqual(len(guards()), 9)
        for path in guards():
            with self.subTest(path.relative_to(REPO).as_posix()):
                crash = probe(path, "ValueError")
                output = (crash.stdout + crash.stderr).decode("utf-8")
                self.assertNotIn(crash.returncode, (0, INTERRUPTED))
                self.assertIn("\u2192 \u00e9t\u00e9", output)
                self.assertIn("by hand: run it again", output)
                self.assertNotIn("Traceback", output)
                self.assertEqual(probe(path, "KeyboardInterrupt").returncode, INTERRUPTED)


if __name__ == "__main__":
    unittest.main()
