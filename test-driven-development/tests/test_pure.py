import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts" / "lib"))
sys.path.insert(0, str(HERE))

import samples
from commands import build, is_dotted, split
from common import GREEN, RED, Outcome
from outcome import judge, parse


class ParseTest(unittest.TestCase):
    def test_pytest_red(self):
        outcome = parse("pytest", samples.PYTEST_RED, 1)
        self.assertEqual((outcome.ran, outcome.failed, outcome.errors), (1, 1, 0))
        self.assertEqual(outcome.names, ["tests/test_tax.py::test_tax_standard"])
        self.assertEqual(outcome.reason, "AssertionError: assert 0 == 12.5")

    def test_pytest_collection_error(self):
        outcome = parse("pytest", samples.PYTEST_COLLECTION, 2)
        self.assertEqual((outcome.ran, outcome.errors), (0, 1))
        self.assertEqual(outcome.reason, "ImportError: cannot import name 'tax' from 'shop'")

    def test_pytest_green_and_empty(self):
        green = parse("pytest", samples.PYTEST_GREEN, 0)
        self.assertEqual((green.ran, green.warnings), (3, 2))
        self.assertEqual(parse("pytest", samples.PYTEST_EMPTY, 5).ran, 0)

    def test_unittest_counts_and_names(self):
        outcome = parse("unittest", samples.UNITTEST_MIXED, 1)
        self.assertEqual((outcome.ran, outcome.failed, outcome.errors), (2, 1, 1))
        self.assertEqual(outcome.names, ["test_tax.TaxTest.test_b", "test_tax.TaxTest.test_a"])

    def test_jest(self):
        red = parse("jest", samples.JEST_RED, 1)
        self.assertEqual((red.ran, red.failed, red.errors), (5, 1, 0))
        self.assertEqual(red.names, [f"Invoice {samples.ANGLE} adds tax"])
        crash = parse("jest", samples.JEST_CRASH, 1)
        self.assertEqual((crash.ran, crash.errors, crash.names), (0, 1, []))
        self.assertEqual(parse("jest", "No tests found, exiting with code 1", 1).ran, 0)

    def test_vitest(self):
        red = parse("vitest", samples.VITEST_RED, 1)
        self.assertEqual((red.ran, red.failed, red.names), (3, 1, ["tests/tax.test.js > tax > adds tax"]))
        suite = parse("vitest", samples.VITEST_SUITE, 1)
        self.assertEqual((suite.ran, suite.errors), (0, 1))
        self.assertEqual(parse("vitest", "No test files found, exiting with code 1", 1).ran, 0)

    def test_cargo(self):
        red = parse("cargo", samples.CARGO_RED, 101)
        self.assertEqual((red.ran, red.failed, red.errors, red.names), (2, 1, 0, ["tax::adds"]))
        self.assertEqual(parse("cargo", samples.CARGO_BUILD, 101).errors, 1)

    def test_go(self):
        red = parse("go", samples.GO_RED, 1)
        self.assertEqual((red.ran, red.failed, red.names), (2, 1, ["TestTax"]))
        broken = parse("go", samples.GO_BUILD, 1)
        self.assertEqual((broken.errors, broken.reason), (1, "./tax_test.go:5:2: undefined: Tax"))

    def test_custom_command_is_sniffed(self):
        self.assertEqual(parse("custom", samples.JEST_RED, 1).failed, 1)
        self.assertEqual(parse("custom", samples.UNITTEST_MIXED, 1).errors, 1)
        self.assertIsNone(parse("custom", "BUILD FAILED", 1).ran)


class JudgeTest(unittest.TestCase):
    def test_red_needs_a_failed_assertion(self):
        self.assertTrue(judge(RED, Outcome(ran=1, failed=1), 1)[0])
        self.assertFalse(judge(RED, Outcome(ran=1), 0)[0])
        self.assertFalse(judge(RED, Outcome(ran=0), 5)[0])
        self.assertFalse(judge(RED, Outcome(ran=1, errors=1), 1)[0])

    def test_green_needs_tests_and_no_failure(self):
        self.assertTrue(judge(GREEN, Outcome(ran=4), 0)[0])
        self.assertFalse(judge(GREEN, Outcome(ran=0), 0)[0])
        self.assertFalse(judge(GREEN, Outcome(ran=4, failed=1), 1)[0])
        self.assertIn("warning", " ".join(judge(GREEN, Outcome(ran=4, warnings=1), 0)[1]))

    def test_unknown_summary(self):
        self.assertFalse(judge(RED, Outcome(), 1)[0])
        self.assertTrue(judge(GREEN, Outcome(), 0)[0])
        self.assertFalse(judge(GREEN, Outcome(), 1)[0])


class CommandTest(unittest.TestCase):
    def test_targets(self):
        self.assertEqual(split("tests\\test_tax.py::TaxTest::test_a"), ("tests/test_tax.py", "TaxTest::test_a"))
        self.assertEqual(split(None), (None, None))
        self.assertTrue(is_dotted("tests.test_tax.TaxTest.test_a"))
        self.assertFalse(is_dotted("tests/test_tax.py"))

    def test_cargo_and_go(self):
        cargo, _ = build("cargo", Path("."), "tests/tax.rs::adds", 2)
        self.assertEqual(cargo, ["cargo", "test", "-j", "2", "--test", "tax", "adds", "--", "--test-threads=2"])
        go, _ = build("go", Path("."), "shop/tax_test.go::TestTax", 1)
        self.assertEqual(go, ["go", "test", "-v", "-p", "1", "./shop", "-run", "^TestTax$"])
        self.assertIn("./...", build("go", Path("."), None, 2)[0])
