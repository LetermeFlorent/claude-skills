import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path[:0] = [str(SCRIPTS / "lib"), str(SCRIPTS)]

import cleanup
from common import START_FILE, new_work, work_folder
from project import digest


def create(root, *names):
    for name in names:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text("x\n", encoding="utf-8")


class Cleanup(unittest.TestCase):
    def test_only_files_created_by_the_run_are_deleted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            create(root, "keep.py", "tests/test_app.py", "tests/test_secureloop_tmp_a.py",
                   "new/deep/secureloop_tmp_b.py", "node_modules/x.js", ".env",
                   "tests/__pycache__/test_secureloop_tmp_a.cpython-313.pyc")
            start = {"files": ["keep.py", "tests/test_app.py"], "ignored": [".env"]}
            lines = cleanup.delete_listed(root, start, ["keep.py", "tests", "tests/test_secureloop_tmp_a.py", ".env",
                                                        "new/deep/secureloop_tmp_b.py", "node_modules/x.js", "../x"])
            self.assertEqual(sum(line.startswith("kept:") for line in lines), 5)
            self.assertEqual(sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()),
                             [".env", "keep.py", "node_modules/x.js", "tests/test_app.py"])

    def test_changed_and_missing_tests_are_seen(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            create(root, "tests/test_a.py", "tests/test_b.py", "tests/test_c.py")
            start = {"tests": {"tests/test_a.py": digest(root / "tests/test_a.py"), "tests/test_b.py": "old",
                               "tests/test_c.py": digest(root / "tests/test_c.py")}}
            (root / "tests/test_c.py").write_bytes(b"x\r\n")
            (root / "tests/test_a.py").unlink()
            self.assertEqual(cleanup.test_changes(root, start), (["tests/test_b.py"], ["tests/test_a.py"]))

    def test_work_folder_is_checked_before_deletion(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, START_FILE).write_text("{}", encoding="utf-8")
            self.assertIsNone(work_folder(folder))
        work = new_work()
        try:
            self.assertIsNone(work_folder(str(work)))
            (work / START_FILE).write_text("{}", encoding="utf-8")
            self.assertEqual(work_folder(str(work)), work.resolve())
        finally:
            for path in work.iterdir():
                path.unlink()
            work.rmdir()


if __name__ == "__main__":
    unittest.main()
