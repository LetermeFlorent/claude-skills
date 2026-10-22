BULLET, ANGLE, RULE = "\u25cf", "\u203a", "\u23af\u23af"

PYTEST_RED = """tests/test_tax.py F
E       AssertionError: assert 0 == 12.5
=========================== short test summary info ============================
FAILED tests/test_tax.py::test_tax_standard - AssertionError: assert 0 == 12.5
============================== 1 failed in 0.05s ===============================
"""
PYTEST_COLLECTION = """E   ImportError: cannot import name 'tax' from 'shop'
ERROR tests/test_tax.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.10s ===============================
"""
PYTEST_GREEN = "========== 3 passed, 2 warnings in 0.03s ==========\n"
PYTEST_EMPTY = "============================ no tests ran in 0.01s =============================\n"
UNITTEST_MIXED = """FE
======================================================================
ERROR: test_b (test_tax.TaxTest.test_b)
NameError: name 'tax' is not defined
======================================================================
FAIL: test_a (test_tax.TaxTest)
AssertionError: 0 != 12.5
----------------------------------------------------------------------
Ran 2 tests in 0.001s

FAILED (failures=1, errors=1, expected failures=3)
"""
JEST_RED = f"""  {BULLET} Invoice {ANGLE} adds tax

    expect(received).toBe(expected) // Object.is equality

Tests:       1 failed, 4 passed, 5 total
Test Suites: 1 failed, 1 total
"""
JEST_CRASH = f"""  {BULLET} Test suite failed to run

    SyntaxError: Unexpected token
Test Suites: 1 failed, 1 total
Tests:       0 total
"""
VITEST_RED = """ FAIL  tests/tax.test.js > tax > adds tax
AssertionError: expected 0 to be 12.5
 Test Files  1 failed (1)
      Tests  1 failed | 2 passed (3)
"""
VITEST_SUITE = f"""\x1b[31m{RULE} Failed Suites 1 {RULE}\x1b[39m
 FAIL  tests/tax.test.js [ tests/tax.test.js ]
Error: Failed to load url ../src/tax
 Test Files  1 failed (1)
      Tests  no tests
"""
CARGO_RED = """running 2 tests
test tax::adds ... FAILED
test tax::keeps ... ok

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
"""
CARGO_BUILD = "error[E0425]: cannot find function `tax` in this scope\nerror: could not compile `shop`\n"
GO_RED = """=== RUN   TestTax
    tax_test.go:9: got 0, want 12.5
--- FAIL: TestTax (0.00s)
=== RUN   TestKeep
--- PASS: TestKeep (0.00s)
FAIL
FAIL\texample.org/shop\t0.002s
"""
GO_BUILD = "# example.org/shop\n./tax_test.go:5:2: undefined: Tax\nFAIL\texample.org/shop [build failed]\n"
