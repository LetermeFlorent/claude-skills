import json
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


if __name__ == "__main__":
    unittest.main()
