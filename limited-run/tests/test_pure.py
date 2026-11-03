import os
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

import memory
import procs
import records

RUN = str(SCRIPTS / "run.py")
WINDOWS = os.name == "nt"
TIMEOUT = 60
SHOW_UP_SECONDS = 15
STEP = 0.2
PRIORITY = ("import ctypes, sys; k = ctypes.windll.kernel32; k.GetCurrentProcess.restype = ctypes.c_void_p; "
            "k.GetPriorityClass.argtypes = [ctypes.c_void_p]; print(k.GetPriorityClass(k.GetCurrentProcess())); "
            "sys.exit(7)") if WINDOWS else "import os, sys; print(os.nice(0)); sys.exit(7)"
LOW_PRIORITY = "16384" if WINDOWS else "10"
FIND_PYTHON = ("Get-CimInstance Win32_Process -Filter \"Name like 'python%' and CommandLine like '%{}%'\" "
               "| ForEach-Object {{ $_.ProcessId }}")


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


class EndToEndTest(TaskFolder):
    def test_exit_code_is_passed_priority_is_low_and_record_removed(self):
        done = self.tool("start", "--name", "short", "--", sys.executable, "-c", PRIORITY)
        self.assertEqual(done.returncode, 7, done.stdout + done.stderr)
        self.assertIn(LOW_PRIORITY, done.stdout.splitlines())
        self.assertIn("limited-run: short pid", done.stdout)
        self.assertEqual(list(self.folder.glob("*.json")), [])

    def test_a_child_over_the_cap_fails(self):
        done = self.tool("start", "--ram-mb", "300", "--", sys.executable, "-c", "b = bytearray(600 * 1024 * 1024)")
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(list(self.folder.glob("*.json")), [])

    def test_background_task_is_listed_then_stopped_with_its_tree(self):
        tag = uuid.uuid4().hex
        script = (f"import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', "
                  f"'import time; time.sleep(60)', '{tag}']); time.sleep(60)")
        launcher = subprocess.Popen([sys.executable, "-I", RUN, "start", "--name", "sleeper", "--", sys.executable,
                                     "-c", script, tag], env=self.env, stdout=subprocess.DEVNULL)
        try:
            self.assertTrue(self.wait_for(lambda: len(self.pythons(tag)) >= 3), "the tree never came up")
            self.assertIn("sleeper", self.tool("list").stdout)
            self.assertIn("stopped sleeper", self.tool("stop", "--all").stdout)
            self.assertTrue(self.wait_for(lambda: not self.pythons(tag)), self.pythons(tag))
            launcher.wait(timeout=TIMEOUT)
            self.assertEqual(list(self.folder.glob("*.json")), [])
        finally:
            launcher.kill()
            launcher.wait(timeout=TIMEOUT)

    def test_a_dead_launcher_takes_its_tree_along(self):
        tag = uuid.uuid4().hex
        launcher = subprocess.Popen([sys.executable, "-I", RUN, "start", "--", sys.executable, "-c",
                                     "import time; time.sleep(60)", tag], env=self.env, stdout=subprocess.DEVNULL)
        self.assertTrue(self.wait_for(lambda: len(self.pythons(tag)) >= 2), "the task never came up")
        launcher.kill()
        launcher.wait(timeout=TIMEOUT)
        self.assertTrue(self.wait_for(lambda: not self.pythons(tag)), self.pythons(tag))
        self.assertIn("0 live task", self.tool("list").stdout)
        self.assertEqual(list(self.folder.glob("*.json")), [])

    def wait_for(self, condition):
        deadline = time.monotonic() + SHOW_UP_SECONDS
        while time.monotonic() < deadline:
            if condition():
                return True
            time.sleep(STEP)
        return condition()

    def pythons(self, tag):
        if WINDOWS:
            found = subprocess.run(["powershell", "-NoProfile", "-Command", FIND_PYTHON.format(tag)],
                                   capture_output=True, text=True, timeout=TIMEOUT).stdout
            return found.split()
        found = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True, timeout=TIMEOUT).stdout
        return [line.split()[0] for line in found.splitlines() if tag in line and "python" in line.lower()]


if __name__ == "__main__":
    unittest.main()
