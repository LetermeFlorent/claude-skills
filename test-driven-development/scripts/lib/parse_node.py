import re

from common import Outcome, counts_of

NODE_COUNT = re.compile(r"(\d+) (failed|passed|skipped|todo)")
JEST_TESTS = re.compile(r"^Tests:\s+(.*)$", re.M)
JEST_EMPTY = "No tests found"
JEST_CRASH = "Test suite failed to run"
JEST_NAME = re.compile(r"^\s*\u25cf (.+?)\s*$", re.M)
VITEST_TESTS = re.compile(r"^\s*Tests\s+(.*)$", re.M)
VITEST_EMPTY = "No test files found"
VITEST_SUITES = re.compile(r"Failed Suites (\d+)")
VITEST_ERRORS = re.compile(r"^\s*Errors\s+(\d+) errors?", re.M)
VITEST_NAME = re.compile(r"^\s*FAIL\s+(.+?)\s*$", re.M)


def jest(text, code):
    if JEST_EMPTY in text:
        return Outcome(ran=0)
    tests = JEST_TESTS.findall(text)
    if not tests:
        return None
    counts = counts_of(NODE_COUNT, tests[-1])
    failed = counts.get("failed", 0)
    names = [name for name in JEST_NAME.findall(text) if name != JEST_CRASH]
    return Outcome(ran=counts.get("passed", 0) + failed, failed=failed, errors=text.count(JEST_CRASH), names=names)


def vitest(text, code):
    if VITEST_EMPTY in text:
        return Outcome(ran=0)
    tests = VITEST_TESTS.findall(text)
    if not tests:
        return None
    counts = counts_of(NODE_COUNT, tests[-1])
    failed = counts.get("failed", 0)
    errors = sum(map(int, VITEST_SUITES.findall(text))) + sum(map(int, VITEST_ERRORS.findall(text)))
    return Outcome(ran=counts.get("passed", 0) + failed, failed=failed, errors=errors,
                   names=VITEST_NAME.findall(text))
