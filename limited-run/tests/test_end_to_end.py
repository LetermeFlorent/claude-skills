import os
import subprocess
import sys
import time
import unittest
import uuid

sys.dont_write_bytecode = True

from test_pure import RUN, TIMEOUT, TaskFolder

WINDOWS = os.name == "nt"
SHOW_UP_SECONDS = 15
STEP = 0.2
PRIORITY = ("import ctypes, sys; k = ctypes.windll.kernel32; k.GetCurrentProcess.restype = ctypes.c_void_p; "
            "k.GetPriorityClass.argtypes = [ctypes.c_void_p]; print(k.GetPriorityClass(k.GetCurrentProcess())); "
            "sys.exit(7)") if WINDOWS else "import os, sys; print(os.nice(0)); sys.exit(7)"
LOW_PRIORITY = "16384" if WINDOWS else "10"
FIND_PYTHON = ("Get-CimInstance Win32_Process -Filter \"Name like 'python%' and CommandLine like '%{}%'\" "
               "| ForEach-Object {{ $_.ProcessId }}")


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

    def test_a_queued_start_waits_for_its_name_then_runs(self):
        holder = subprocess.Popen([sys.executable, "-I", RUN, "start", "--name", "lock", "--", sys.executable, "-c",
                                   "import time; time.sleep(8)"], env=self.env, stdout=subprocess.DEVNULL)
        try:
            self.assertTrue(self.wait_for(lambda: (self.folder / "lock.json").exists()),
                            "the holder never claimed the name")
            refused = self.tool("start", "--name", "lock", "--queue", "1", "--", sys.executable, "-c", "pass")
            self.assertEqual(refused.returncode, 2, refused.stdout)
            queued = self.tool("start", "--name", "lock", "--queue", "30", "--", sys.executable, "-c",
                               "print('second')")
            self.assertEqual(queued.returncode, 0, queued.stdout + queued.stderr)
            self.assertEqual(queued.stdout.count("limited-run: waiting for lock"), 1)
            self.assertIn("second", queued.stdout.splitlines())
        finally:
            holder.kill()
            holder.wait(timeout=TIMEOUT)

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
