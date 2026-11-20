import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

import blender
import docsite
import gate_rules
import livequeue
import run


class FindBlender(unittest.TestCase):
    def test_env_wins(self):
        self.assertEqual(blender.find_blender({"BLENDER_EXE": __file__}, lambda _: "x", lambda _: []), __file__)

    def test_env_missing_file(self):
        self.assertIsNone(blender.find_blender({"BLENDER_EXE": "/no/such"}, lambda _: "x", lambda _: []))

    def test_path_then_search(self):
        self.assertEqual(blender.find_blender({}, lambda _: "/bin/blender", lambda _: []), "/bin/blender")
        hits = {"blender-4.2": ["a/blender-4.2/blender.exe"], "blender-*": ["b/4.5", "b/5.3"]}
        found = blender.find_blender({}, lambda _: None, lambda glob: hits["blender-*"] if "Tools" in glob else [])
        self.assertEqual(found, "b/5.3")

    def test_nothing(self):
        self.assertIsNone(blender.find_blender({}, lambda _: None, lambda _: []))


class Command(unittest.TestCase):
    def test_blend_opened_and_args_after_dash(self):
        argv = blender.command("blender", "a.blend", "run_bl.py", ["s.py", 3])
        self.assertIn("--factory-startup", argv)
        self.assertLess(argv.index("a.blend"), argv.index("--python"))
        self.assertEqual(argv[-3:], ["--", "s.py", "3"])

    def test_model_file_not_opened(self):
        self.assertNotIn("a.glb", blender.command("blender", "a.glb", "x.py", [])[:-1])

    def test_keep_prefs(self):
        with mock.patch.dict(os.environ, {"BLENDER_KEEP_PREFS": "1"}):
            self.assertNotIn("--factory-startup", blender.command("b", None, "x.py", []))


class Output(unittest.TestCase):
    LOG = ("Blender 5.3.0\n@@ shot front a.png\nhello\n10:50:52 | INFO: Starting\n"
           "INFO Draco is available\nRead blend: x\n")

    def test_marked_only(self):
        self.assertEqual(blender.useful(self.LOG), ["shot front a.png"])

    def test_errors_from_traceback(self):
        log = "x\nTraceback (most recent call last):\n  File y\nRuntimeError: poll() failed\n"
        self.assertEqual(blender.errors(log)[-1], "RuntimeError: poll() failed")


class Docs(unittest.TestCase):
    DATA = {"titles": ["Bevel Modifier", "Mesh Bevel", "Array"],
            "docnames": ["mod/bevel", "mesh/bevel", "mod/array"],
            "titleterms": {"bevel": [0, 1], "modifi": 0}, "terms": {"bevel": [0, 1], "modifi": [0, 2]}}

    def test_search_ranks_pages_with_all_words(self):
        hits = docsite.search(self.DATA, "bevel modifiers")
        self.assertEqual(hits[0][2], "mod/bevel.html")
        self.assertEqual(len(hits), 3)

    def test_find_lines_groups(self):
        text = "\n".join(f"line {n}" for n in range(30)) + "\nUDIM here"
        shown = docsite.find_lines(text, "udim")
        self.assertEqual(shown[-1], "UDIM here")
        self.assertNotIn("...", shown)

    def test_article_only(self):
        reader = docsite.Article()
        reader.feed("<nav>menu</nav><article role='main'><h1>Bevel</h1><p>Width</p><script>x</script></article>")
        self.assertEqual("".join(reader.parts).split(), ["Bevel", "Width"])


class Live(unittest.TestCase):
    def test_alive(self):
        self.assertTrue(livequeue.alive(os.getpid()))

    def test_no_window_without_ready_file(self):
        self.assertIsNone(livequeue.running_pid(Path(__file__).parent / "no-such-queue"))

    def test_shots_command_targets_shots_script(self):
        argv = livequeue.shots_command("snap.blend", ["out", "--size", "64"])
        self.assertEqual(Path(argv[2]).name, "shots.py")
        self.assertEqual(argv[3:], ["snap.blend", "out", "--size", "64"])


class RunChecks(unittest.TestCase):
    def check(self, *argv):
        with self.assertRaises(SystemExit) as stop:
            run.check(run.parse(list(argv)))
        return stop.exception.code

    def test_refuses_save_over_source(self):
        self.assertEqual(self.check(__file__, __file__, "--save", __file__), 2)

    def test_refuses_missing_script_and_bad_save(self):
        self.assertEqual(self.check("-", "/no/script.py", "--save", "out.txt"), 2)

    def test_accepts_empty_scene(self):
        self.assertEqual(run.check(run.parse(["-", __file__]))[0], "-")


class GateRules(unittest.TestCase):
    def test_rows(self):
        self.assertEqual(gate_rules.parse_rows(["Back:Plates:12"]), ({"Back:Plates": 12}, None))
        self.assertIsNotNone(gate_rules.parse_rows(["Plates"])[1])

    def test_measure_line(self):
        self.assertEqual(gate_rules.parse_measure("measure belly Body 1.2"), ("belly", "Body", 1.2))
        self.assertIsNone(gate_rules.parse_measure("imported with x"))

    def test_verdicts(self):
        measures = [("belly", "Body", 1.0), ("body_bend", "Body", 2.0), ("count", "Plates", 9), ("other", "x", 0)]
        refused, kept = gate_rules.verdicts(measures, {"Plates": 12})
        self.assertEqual(kept, 1)
        self.assertEqual(len(refused), 2)
        self.assertIn("design sheet says 12", refused[1])


if __name__ == "__main__":
    unittest.main()
