import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

from parse import commit_paths, split_tasks, strip_range, task_files
from placement import check_location, excluded
from rules import check_header, check_task, check_text

HEADER = """# Cart plan

Goal: add a cart total.
Architecture: one pure module.
Stack: python
Spec: .ia/specs/2026-10-22-cart.md

## Global constraints

- files under 150 lines

## Review focus

- empty cart returns zero
"""

TASK = """### Task 1: Total

Files:
- Create: `src/total.py` (about 40 lines)
- Test: `tests/test_total.py`

- [ ] Step 1: Write the failing test

```python
def test_total():
    assert total([]) == 0
```

- [ ] Step 2: Run the test and watch it fail

Run: `python -m unittest tests.test_total`
Expected: FAIL

- [ ] Step 3: Write the code

- [ ] Step 4: Run the test and watch it pass

- [ ] Step 5: Commit through clean-commits

Paths: `src/total.py`, `tests/test_total.py`
Intent: add the cart total
"""


def problems(task_text):
    _, tasks = split_tasks(task_text)
    return check_task(tasks[0])


class ParseTest(unittest.TestCase):
    def test_tasks_and_files(self):
        header, tasks = split_tasks(HEADER + TASK)
        self.assertIn("Goal:", header)
        self.assertEqual(len(tasks), 1)
        kinds = [(kind, path) for kind, path, _ in task_files(tasks[0]["body"])]
        self.assertEqual(kinds, [("Create", "src/total.py"), ("Test", "tests/test_total.py")])

    def test_line_range_is_dropped(self):
        self.assertEqual(strip_range("src/a.py:12-40"), "src/a.py")

    def test_commit_paths(self):
        self.assertEqual(commit_paths("Paths: `a.py`, `b.py:3-4`"), {"a.py", "b.py"})
        self.assertIsNone(commit_paths("nothing here"))


class RulesTest(unittest.TestCase):
    def test_good_plan_passes(self):
        self.assertEqual(check_header(HEADER), [])
        self.assertEqual(problems(TASK), [])
        self.assertEqual(check_text(HEADER + TASK), [])

    def test_missing_header_parts(self):
        found = check_header("# Plan\n\nGoal: x\n")
        self.assertEqual(len(found), 5)

    def test_missing_commit_path(self):
        found = problems(TASK.replace("`src/total.py`, `tests/test_total.py`", "`src/total.py`"))
        self.assertTrue(any("tests/test_total.py" in item for item in found))

    def test_oversized_file(self):
        self.assertTrue(any("limit" in item for item in problems(TASK.replace("40 lines", "400 lines"))))

    def test_test_first(self):
        swapped = TASK.replace("Write the failing test", "Write the code").replace("Write the code\n\n```", "x\n\n```")
        self.assertTrue(any("failing test" in item for item in problems(swapped)))

    def test_no_test_needs_a_reason(self):
        bare = TASK.replace("- Test: `tests/test_total.py`\n", "").replace(", `tests/test_total.py`", "")
        self.assertTrue(any("No test" in item for item in problems(bare)))
        reasoned = bare.replace("Files:", "No test: pure documentation\nFiles:")
        self.assertFalse(any("No test" in item for item in problems(reasoned)))

    def test_commit_goes_through_clean_commits(self):
        found = problems(TASK.replace("through clean-commits", "with git"))
        self.assertTrue(any("clean-commits" in item for item in found))

    def test_forbidden_text(self):
        for bad in ("git add .", "git add -A", "git commit -am x", "git push origin main", "git commit --no-verify",
                    "Co-Authored-By: someone", "TODO later", "Similar to Task 2", "a\u2014b"):
            self.assertTrue(check_text(bad), bad)
        self.assertEqual(check_text("git add src/total.py tests/test_total.py"), [])


class PlacementTest(unittest.TestCase):
    def test_location(self):
        bad, _ = check_location(Path("docs/plans/2026-10-22-cart.md"))
        self.assertTrue(bad)
        good, root = check_location(Path("repo/.ia/plans/2026-10-22-cart.md"))
        self.assertEqual(good, [])
        self.assertEqual(root.name, "repo")
        misnamed, _ = check_location(Path("repo/.ia/plans/cart.md"))
        self.assertTrue(misnamed)

    def test_exclude_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            self.assertFalse(excluded(root))
            with open(root / ".git" / "info" / "exclude", "a", encoding="utf-8") as handle:
                handle.write("\n.ia\n")
            self.assertTrue(excluded(root))


if __name__ == "__main__":
    unittest.main()
