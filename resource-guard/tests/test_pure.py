import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

import limits
import linuxmetrics
import macmetrics
from heavy import is_heavy
from payload import command_of

GUARD = SCRIPTS / "guard.py"
RUN_TIMEOUT = 60
LINE = re.compile(r"^resource-guard: ram (\d+\.\d GB free|unknown), cpu (\d+ %|unknown), "
                  r"disk (\d+ % busy|unknown), \S+ (\d+ GB free|unknown): (ok|wait \(.+\))$")
HEAVY = (
    "npm test", "npm run build", "pnpm install", "yarn", "yarn add react", "bun run dev", "npx vite build",
    "cd app && npm ci", "docker compose up -d", "docker-compose build", "python -m pytest", "pytest -x",
    "C:/Python312/python.exe x.py", "./gradlew test", "mvn package", "cargo build --release", "go test ./...",
    "dotnet build", "tsc --noEmit", "FOO=1 vitest run", "sudo nice -n 10 make -j2", "bash -lc 'npm run build'",
    "./build.sh", "git pull; node server.js", "jest --ci", "npx playwright test", "webpack", "pnpm tauri dev",
    "java -jar app.jar", "py -3 setup.py", "./test",
    "python -I C:/x/limited-run/scripts/run.py start --name foo -- npm test",
    'python -I "C:/x/limited-run/scripts/run.py" start --cwd C:/p -- npx vite',
    "python -I C:/x/browser-bidi/scripts/launch.py --url x",
    "python -I C:/x/browser-bidi/scripts/measure_images.py --url x",
    'python -I "$S/bidi.py" shot a.png --port 9300 && npm run build',
)
LIGHT = (
    "", "ls -la", "git status", 'git commit -m "run the test suite"', "cat build.log", "echo hello",
    "npm --version", "go version", "grep -r docker .", "rg test src", "npm info react", "gofmt -l .",
    "test -f package.json", "nodemon-config", "python -I C:/x/resource-guard/scripts/guard.py wait",
    'python -I "$S/bidi.py" shot a.png --port 9300', "python -I C:/x/limited-run/scripts/run.py list",
    'python -I "C:/x/limited-run/scripts/run.py" stop --all',
    'python -I "C:/x/clean-code/scripts/findings.py" --run "C:/p/.ia/clean-code/r1" list',
    r"py -3 C:\x\strip-ai-traces\scripts\scan.py a.md --no-git",
    'python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/progress-board/server.py" start',
)


class HeavyTest(unittest.TestCase):
    def test_heavy_commands(self):
        for command in HEAVY:
            self.assertTrue(is_heavy(command), command)

    def test_light_commands(self):
        for command in LIGHT:
            self.assertFalse(is_heavy(command), command)


class PayloadTest(unittest.TestCase):
    def test_every_accepted_shape(self):
        shapes = (
            ({"tool_name": "Bash", "tool_input": {"command": "npm test"}}, "npm test"),
            ({"tool_input": {"cmd": "npm test"}}, "npm test"),
            ({"tool_input": {"command": ["npm", "test"]}}, "npm test"),
            ({"tool_input": {"command": ["bash", "-lc", "npm test"]}}, "npm test"),
            ({"tool_input": {"command": ["C:/x/pwsh.exe", "-Command", "npm test"]}}, "npm test"),
            ({"command": "npm test"}, "npm test"),
            ({"command": ["cmd", "/c", "npm test"]}, "npm test"),
        )
        for event, expected in shapes:
            self.assertEqual(command_of(event), expected, event)

    def test_odd_payloads_give_nothing(self):
        for event in (None, [], "npm test", {}, {"tool_input": "npm test"}, {"tool_input": {"command": 3}},
                      {"command": [1, 2]}, {"tool_input": {"file_path": "a.py"}}):
            self.assertEqual(command_of(event), "", event)


class LimitsTest(unittest.TestCase):
    def test_flag_beats_env_beats_default(self):
        env = {"RESOURCE_GUARD_CPU": "70", "RESOURCE_GUARD_RAM_GB": "3", "RESOURCE_GUARD_DISK": "oops"}
        chosen = limits.resolve({"cpu": 50.0, "ram_gb": None}, env)
        self.assertEqual((chosen["cpu"], chosen["ram_gb"], chosen["disk"]), (50.0, 3.0, 100.0))
        self.assertEqual(limits.resolve({}, {}), limits.DEFAULTS)
        self.assertEqual(limits.resolve({}, {"RESOURCE_GUARD_TIMEOUT": "-5"})["timeout"], 300.0)

    def test_verdicts(self):
        chosen = limits.resolve({}, {})
        calm = {"ram_gb": 6.2, "cpu": 34.0, "disk": 12.0, "drive": "C:", "free_gb": 48.0}
        self.assertEqual(limits.reasons(calm, chosen), [])
        self.assertEqual(limits.status_line(calm, []),
                         "resource-guard: ram 6.2 GB free, cpu 34 %, disk 12 % busy, C: 48 GB free: ok")
        busy = dict(calm, ram_gb=1.2, cpu=92.0, disk=130.0)
        found = limits.reasons(busy, chosen)
        self.assertEqual(found, ["ram 1.2 GB < 1.5 GB", "cpu 92 % > 85 %", "disk 130 % busy > 100 %"])
        self.assertTrue(limits.status_line(busy, found).endswith(": wait (ram 1.2 GB < 1.5 GB, cpu 92 % > 85 %, "
                                                                 "disk 130 % busy > 100 %)"))

    def test_unknown_never_blocks_and_low_disk_only_warns(self):
        chosen = limits.resolve({}, {})
        blind = {"ram_gb": None, "cpu": None, "disk": None, "drive": "C:", "free_gb": 5.0}
        self.assertEqual(limits.reasons(blind, chosen), [])
        self.assertTrue(limits.low_disk(blind, chosen))
        self.assertIn("ram unknown", limits.describe(blind))


class PlatformParsingTest(unittest.TestCase):
    def test_linux_proc_files(self):
        self.assertAlmostEqual(linuxmetrics.available_gb("MemTotal: 8 kB\nMemAvailable: 2097152 kB\n"), 2.0)
        first = linuxmetrics.cpu_ticks("cpu  100 0 100 700 100 0 0 0 0 0\ncpu0 1 1 1 1 1 1 1 1")
        second = linuxmetrics.cpu_ticks("cpu  150 0 100 750 100 0 0 0 0 0\n")
        self.assertAlmostEqual(linuxmetrics.cpu_busy(first, second), 50.0)
        line = "   8       0 sda 1 0 0 0 0 0 0 0 0 {} 0"
        before = linuxmetrics.disk_ticks(line.format(1000), lambda name: True)
        after = linuxmetrics.disk_ticks(line.format(1250), lambda name: True)
        self.assertAlmostEqual(linuxmetrics.disk_busy(before, after, 0.5), 50.0)

    def test_mac_vm_stat(self):
        text = "Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 65536.\nPages inactive: 65536."
        self.assertAlmostEqual(macmetrics.free_gb(text), 2.0)
        self.assertAlmostEqual(macmetrics.load_percent(2.0, 4), 50.0)


class SmokeTest(unittest.TestCase):
    def run_guard(self, arguments, given=""):
        return subprocess.run([sys.executable, "-I", str(GUARD), *arguments], input=given, capture_output=True,
                              text=True, timeout=RUN_TIMEOUT)

    def test_real_check(self):
        done = self.run_guard(["check"])
        self.assertIn(done.returncode, (0, 1), done.stderr)
        self.assertRegex(done.stdout.splitlines()[0], LINE)

    def test_hook_lets_light_and_unreadable_calls_through_silently(self):
        for given in ('{"tool_name": "Bash", "tool_input": {"command": "git status"}}', "not json", ""):
            done = self.run_guard(["hook"], given)
            self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""), given)


if __name__ == "__main__":
    unittest.main()
