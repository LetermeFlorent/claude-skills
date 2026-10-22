import re

from common import RED, Outcome
from parse_native import cargo, go
from parse_node import jest, vitest
from parse_python import pytest, unittest

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
REASON = re.compile(r"^(?:E[ \t]+(.+)|[ \t]*(?!.*Failed to import test module)((?:\w+\.)*\w*(?:Error|Exception)\b.*"
                    r"|expect\(received\).*|.*panicked at .*|.*undefined: .*))$", re.M)
PARSERS = {"pytest": pytest, "unittest": unittest, "jest": jest, "vitest": vitest, "cargo": cargo, "go": go}
SNIFF_ORDER = (jest, vitest, cargo, unittest, pytest, go)
NO_TEST = "no test ran: the id or the path matches no test"
BROKEN = ("the run stopped on an error before any assertion: a typo, a wrong import path or a missing fixture "
          "is a broken test, not a red. When the missing name is the one about to be written, give it an empty "
          "body and run again until the test fails on its assertion")
PASSED_EARLY = ("the test passed before the code exists: it checks behaviour that is already there, or nothing. "
                "Rewrite it until it fails")
UNCHECKED_RED = ("this runner's summary is unknown here, so a failed assertion cannot be told from a crash: read "
                 "the output, and say in the report which assertion failed")
UNCHECKED_GREEN = "this runner's summary is unknown here: exit code 0, read the output to confirm tests ran"


def _sniff(text, code):
    return next((found for found in (parser(text, code) for parser in SNIFF_ORDER) if found), None)


def parse(runner, output, code):
    text = ANSI.sub("", output)
    parser = PARSERS.get(runner)
    outcome = (parser(text, code) if parser else _sniff(text, code)) or Outcome()
    found = REASON.search(text)
    outcome.reason = next(group for group in found.groups() if group).strip() if found else None
    return outcome


def _red_problems(outcome):
    if outcome.errors:
        return [f"{outcome.errors} error(s): {BROKEN}"]
    if not outcome.ran:
        return [NO_TEST]
    return [] if outcome.failed else [PASSED_EARLY]


def _green_problems(outcome):
    if outcome.failed or outcome.errors:
        return [f"not green: {outcome.failed} failed, {outcome.errors} error(s)"]
    return [] if outcome.ran else [NO_TEST]


def _success(expect, outcome):
    if expect == RED:
        return [f"red as expected: {outcome.failed} failed of {outcome.ran}"]
    lines = [f"green: {outcome.ran} passed"]
    if outcome.warnings:
        lines.append(f"{outcome.warnings} warning(s) in the output: read them, fix the ones this change caused")
    return lines


def judge(expect, outcome, code):
    if outcome.ran is None:
        if expect == RED:
            return False, [UNCHECKED_RED]
        return code == 0, [UNCHECKED_GREEN if code == 0 else f"not green: exit code {code}"]
    problems = _red_problems(outcome) if expect == RED else _green_problems(outcome)
    return not problems, problems or _success(expect, outcome)
