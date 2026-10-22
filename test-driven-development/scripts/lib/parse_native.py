import re

from common import Outcome

CARGO_RESULT = re.compile(r"^test result: \w+\. (\d+) passed; (\d+) failed;", re.M)
CARGO_NAME = re.compile(r"^test (\S+) \.\.\. FAILED\s*$", re.M)
CARGO_BUILD = re.compile(r"^error(\[E\d+\])?: ", re.M)
GO_PASS = re.compile(r"^\s*--- PASS: ", re.M)
GO_FAIL = re.compile(r"^\s*--- FAIL: (\S+)", re.M)
GO_BUILD = re.compile(r"\[(build|setup) failed\]")
GO_SUMMARY = re.compile(r"^(ok|FAIL|\?)\s+\S+", re.M)


def cargo(text, code):
    results = CARGO_RESULT.findall(text)
    if not results:
        return Outcome(ran=0, errors=1) if CARGO_BUILD.search(text) else None
    passed = sum(int(count) for count, _ in results)
    failed = sum(int(count) for _, count in results)
    return Outcome(ran=passed + failed, failed=failed, names=CARGO_NAME.findall(text))


def go(text, code):
    broken = len(GO_BUILD.findall(text))
    if not broken and not GO_SUMMARY.search(text):
        return None
    names = GO_FAIL.findall(text)
    return Outcome(ran=len(GO_PASS.findall(text)) + len(names), failed=len(names), errors=broken, names=names)
