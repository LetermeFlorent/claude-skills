import re

from common import Outcome, counts_of

PYTEST_LINE = re.compile(r"^[=\s]*((?:\d+ \w+,? ?)+|no tests ran)\s+in\s+[\d.]+s", re.M)
PYTEST_COUNT = re.compile(r"(\d+) (passed|failed|errors?|warnings?|skipped|xfailed|xpassed|deselected)")
PYTEST_NAME = re.compile(r"^(?:FAILED|ERROR) (\S+)", re.M)
PYTEST_RAN = ("passed", "failed", "xfailed", "xpassed")
UNITTEST_RAN = re.compile(r"^Ran (\d+) tests? in", re.M)
UNITTEST_RESULT = re.compile(r"^FAILED \((.*)\)\s*$", re.M)
UNITTEST_NAME = re.compile(r"^(?:FAIL|ERROR): (\S+) \(([^)]*)\)", re.M)


def pytest(text, code):
    lines = PYTEST_LINE.findall(text)
    if not lines:
        return None
    counts = counts_of(PYTEST_COUNT, lines[-1])
    return Outcome(ran=sum(counts.get(key, 0) for key in PYTEST_RAN), failed=counts.get("failed", 0),
                   errors=counts.get("error", 0), warnings=counts.get("warning", 0),
                   names=PYTEST_NAME.findall(text))


def _unittest_counts(text):
    results = UNITTEST_RESULT.findall(text)
    if not results:
        return {}
    pairs = (piece.rsplit("=", 1) for piece in results[-1].split(", ") if "=" in piece)
    return {key.strip(): int(value) for key, value in pairs if value.strip().isdigit()}


def _unittest_name(short, qualified):
    return qualified if qualified.endswith(short) else f"{qualified}.{short}"


def unittest(text, code):
    ran = UNITTEST_RAN.findall(text)
    if not ran:
        return None
    counts = _unittest_counts(text)
    names = [_unittest_name(short, qualified) for short, qualified in UNITTEST_NAME.findall(text)]
    return Outcome(ran=int(ran[-1]), failed=counts.get("failures", 0), errors=counts.get("errors", 0), names=names)
