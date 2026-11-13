import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

import memory
import procs
import records
import tree

RUN = str(SCRIPTS / "run.py")
TIMEOUT = 60


class TaskFolder(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="limited-run-test-")
        self.folder = Path(self.temp.name)
        self.env = {**os.environ, records.ENV: self.temp.name}

    def tearDown(self):
        for path in self.folder.glob("*.json"):
            if (records.read(path) or {}).get("launcher_pid") == os.getpid():
                path.unlink()
        self.tool("stop", "--all")
        self.temp.cleanup()

    def tool(self, *arguments):
        return subprocess.run([sys.executable, "-I", RUN, *arguments], env=self.env, capture_output=True,
                              text=True, timeout=TIMEOUT)

    def mine(self):
        return {"launcher_pid": os.getpid(), "launcher_created": procs.identity(os.getpid()), "started": 1}


class CapTest(unittest.TestCase):
    def test_cap_is_half_the_free_ram_within_bounds(self):
        self.assertEqual([memory.cap_mb(free) for free in (100, 3000, 20000, None)],
                         [memory.MIN_MB, 1500, memory.MAX_MB, memory.UNKNOWN_MB])

    def test_meminfo_and_live_reading(self):
        self.assertEqual(memory.parse_meminfo("MemTotal: 8000000 kB\nMemAvailable:    2048000 kB\n"), 2000)
        self.assertIsNone(memory.parse_meminfo("MemTotal: 8000000 kB\n"))
        self.assertGreater(memory.free_mb(), 0)


class RecordTest(TaskFolder):
    def test_names_come_from_the_first_word_with_a_counter(self):
        self.assertEqual(records.base_name(["C:/Tools/Node.EXE", "x"]), "node")
        self.assertEqual(records.base_name([""]), "task")
        first = records.claim_next(self.folder, ["npm", "run", "dev"], self.mine())
        second = records.claim_next(self.folder, ["npm", "test"], self.mine())
        self.assertEqual((first, second), ("npm-1", "npm-2"))

    def test_a_live_name_is_refused_and_a_dead_one_is_taken_over(self):
        self.assertTrue(records.claim(self.folder, "web", self.mine()))
        self.assertFalse(records.claim(self.folder, "web", self.mine()))
        self.assertTrue(records.claim(self.folder, "old", {**self.mine(), "launcher_created": -1}))
        self.assertTrue(records.claim(self.folder, "old", self.mine()))
        self.assertEqual([records.valid_name(name) for name in ("bad name", "vite-1", "")], [False, True, False])

    def test_a_dead_record_swapped_for_a_live_one_is_kept(self):
        path = self.folder / "race.json"
        records.claim(self.folder, "race", {**self.mine(), "launcher_created": -1})
        real, raced = records.read, []

        def racing(target):
            found = real(target)
            if target == path and not raced:
                raced.append(True)
                path.unlink()
                records.claim(self.folder, "race", {**self.mine(), "tag": "first"})
            return found

        with mock.patch.object(records, "read", racing):
            self.assertFalse(records.claim(self.folder, "race", {**self.mine(), "tag": "second"}))
        self.assertEqual(records.read(path)["tag"], "first")
        self.assertEqual(sorted(item.name for item in self.folder.iterdir()), ["race.json"])

    def test_stop_skips_a_child_whose_pid_was_reused(self):
        record = {"launcher_pid": os.getpid(), "child_pid": os.getpid()}
        with mock.patch.object(tree, "WINDOWS", False), mock.patch.object(tree, "kill_group") as killed:
            tree.kill_recorded({**record, "child_created": -1})
            killed.assert_not_called()
            tree.kill_recorded({**record, "child_created": procs.identity(os.getpid())})
            killed.assert_called_once_with(os.getpid())

    def test_write_read_update_prune(self):
        records.claim(self.folder, "live", self.mine())
        records.claim(self.folder, "gone", {**self.mine(), "launcher_created": -1})
        records.update(self.folder, "live", {"child_pid": 42})
        found = records.live_records(self.folder)
        self.assertEqual([(item["name"], item["child_pid"]) for item in found], [("live", 42)])
        self.assertFalse((self.folder / "gone.json").exists())
        records.release(self.folder, "live", os.getpid() + 1)
        self.assertTrue((self.folder / "live.json").exists())
        records.release(self.folder, "live", os.getpid())
        self.assertEqual(list(self.folder.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
