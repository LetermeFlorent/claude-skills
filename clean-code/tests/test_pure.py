import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

import common
import lexer
import runs
import words


class CompactTest(unittest.TestCase):
    def test_neighbours_join_into_spans(self):
        self.assertEqual(common.compact([3, 1, 2, 5, 7, 6, 9]), "1-3, 5-7, 9")

    def test_duplicates_count_once(self):
        self.assertEqual(common.compact([4, 4, 4]), "4")


class WordsTest(unittest.TestCase):
    def test_french_segment_in_camel_case(self):
        self.assertTrue(words.french("prixTotal"))

    def test_accent_marks_french(self):
        self.assertTrue(words.french("créerCompte"))

    def test_english_identifier_passes(self):
        self.assertFalse(words.french("userName"))

    def test_french_sentence_found(self):
        self.assertTrue(words.french_text("Votre panier est vide"))

    def test_english_sentence_passes(self):
        self.assertFalse(words.french_text("Your cart is empty"))

    def test_single_word_is_not_a_sentence(self):
        self.assertFalse(words.french_text("panier"))

    def test_ai_trailer_found(self):
        self.assertTrue(words.AI_SIGNATURE.search("Fix\n\nCo-Authored-By: Claude <noreply@anthropic.com>"))

    def test_human_trailer_passes(self):
        self.assertIsNone(words.AI_SIGNATURE.search("Fix\n\nCo-Authored-By: Jane <jane@example.com>"))


class LexerTest(unittest.TestCase):
    def test_directive_kept(self):
        self.assertTrue(lexer.is_directive("# noqa: E501"))

    def test_plain_comment_is_not_a_directive(self):
        self.assertFalse(lexer.is_directive("# compute the total"))

    def test_balance_counts_open_brackets(self):
        self.assertEqual(lexer.balance("f(a[1], {b})"), 0)
        self.assertEqual(lexer.balance("f(a["), 2)


class RunsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_out_folder_holds_the_run(self):
        out = self.root / "elsewhere"
        run = runs.new_run(self.root, str(out))
        self.assertEqual(run.parent, out.resolve())
        self.assertEqual(runs.runs(self.root, str(out)), [run])
        self.assertFalse((self.root / ".ia").exists())

    def test_no_audit_yet_lists_nothing(self):
        self.assertEqual(runs.runs(self.root), [])

    def test_wanted_run_without_findings_is_refused(self):
        with self.assertRaises(FileNotFoundError):
            runs.latest_run(self.root, str(self.root))

    def test_config_overrides_defaults(self):
        folder = self.root.joinpath(*runs.TOOL_PARTS)
        folder.mkdir(parents=True)
        (folder / runs.CONFIG_NAME).write_text(json.dumps({"max_lines": 200}), encoding="utf-8")
        config = runs.load_config(self.root)
        self.assertEqual(config["max_lines"], 200)
        self.assertEqual(config["max_files"], runs.DEFAULTS["max_files"])


class MeasureTest(unittest.TestCase):
    def test_several_scopes_are_measured_together(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("a", "b", "c"):
                (root / name).mkdir()
                (root / name / "mod.py").write_text("VALUE = 1\n", encoding="utf-8")
            out = root / "runs"
            subprocess.run([sys.executable, "-I", str(SCRIPTS / "measure.py"), str(root / "a" / "mod.py"),
                            str(root / "b"), "--out", str(out)], check=True, capture_output=True)
            report = json.loads((runs.runs(root, str(out))[0] / runs.MEASURE).read_text(encoding="utf-8"))
            self.assertEqual(report["stats"]["code_files"], 2)
            self.assertEqual(report["scope"], "a/mod.py, b")


class StoreTest(unittest.TestCase):
    def test_swap_retries_a_busy_target(self):
        import store
        real, calls = store.os.replace, []

        def busy_once(source, target):
            calls.append(target)
            if len(calls) == 1:
                raise PermissionError("in use")
            real(source, target)

        with tempfile.TemporaryDirectory() as base:
            scratch, path = Path(base, "a.tmp"), Path(base, "a.json")
            scratch.write_text("{}", encoding="utf-8")
            store.os.replace = busy_once
            try:
                store._swap(scratch, path)
            finally:
                store.os.replace = real
            self.assertEqual((len(calls), path.read_text(encoding="utf-8")), (2, "{}"))


if __name__ == "__main__":
    unittest.main()
