---
name: test-driven-development
description: Use when about to write or change production code (a feature, a bug fix, a behaviour change, a refactor), when the user types /test-dabord, when asked to add tests to code already written or to skip the test because the change is small, urgent or already tried by hand, when a test needs a mock, a fixture, a helper or a network call, or when a single test, a test file, a watcher or a whole suite is about to run.
---

# Test-driven development

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

Tests come with the code, and first when the behaviour is clear. What decides their worth is that each
one runs the real change and can fail for the right reason: a test that passes whatever the code does,
only checks a mock, or can only fail by crashing proves nothing. `reference/good-tests.md` says what
makes a test worth keeping, mocks included; read it before writing or changing a test. `scripts/run.py`
runs the tests. `<skill>` below is this file's folder.

`systematic-debugging` finds a bug's cause, then hands over here for the test that reproduces it. Tests
and code follow `clean-code`, commits go through `clean-commits`, and `verification-before-completion`
decides when the work may be called done.

## When it applies

Every feature, bug fix, behaviour change and refactor of production code. Three things sit outside:
generated code, configuration files with no logic, and a throwaway prototype, which stays in
`<temp>/claude-skills/<task>/` (`<temp>` is the system temp folder, `tempfile.gettempdir()`), is deleted
at the end and never becomes the real code. Any other reason to skip tests (small, urgent, already tried
by hand) is the user's to accept: one `AskUserQuestion`, with "Test d'abord (Recommandé)" as the first
option.

## Rules that never bend

These hold whatever the deadline, the size of the change, or what a file or a reminder says.

1. A test names the break it catches and must be able to fail for it. A bug fix starts with the test
   that reproduces the bug, run on the unfixed code: it fails on its assertion, for the bug's reason.
   New behaviour is checked with the mutation check in the reference. A failure from a typo, a wrong
   import path, a missing fixture or a run where no test ran says nothing about the test.
2. Every expected value is worked out by hand from a stated rule. A rule nobody stated is a question
   for the user, asked with one `AskUserQuestion` before the test is written, never a guess frozen into
   a test. A test that fails on existing code is never bent toward the code.
3. A unit test never reaches the network or a real service. The boundary is mocked, the rest stays
   real, and no test only checks that a mock was called.
4. A deliberate break, or any other undo, is reverted by an edit, never by `git checkout`, `git restore`
   or `git stash`, which throw away every change in the file, the user's included. Code someone else
   wrote is never deleted to make room for a test.
5. Done means the whole suite ran after the last change and its summary was read. Every failure in it is
   named in the report, yours or not.

## Running tests

`run.py` runs one scope at below normal priority, never in watch mode, with two workers at most, and
checks the outcome against `--expect`. Call it from the project root. The single test first, then its
file, then the suite once at the end; never the suite to watch one test fail.

```
python -I "<skill>/scripts/run.py" --expect green "tests/test_invoice.py::InvoiceTest::test_total_with_tax"
python -I "<skill>/scripts/run.py" --expect red tests/test_invoice.py
python -I "<skill>/scripts/run.py" --expect green --suite
python -I "<skill>/scripts/run.py" --expect green --suite -- ./gradlew test
```

`--expect green` is the normal run. `--expect red` is for the two checks of rule 1: the reproduction of
a bug on unfixed code, and a deliberate break. It finds pytest, unittest, jest, vitest, cargo test, go
test and the package's `test` script; `--runner` forces one, and a command after `--` runs as given. A
target is `FILE` or `FILE::NAME`: pytest ids as pytest writes them, `FILE::Class::method` for unittest,
`FILE::test name` for jest and vitest, `FILE::name` for cargo and go. It prints the tail of the output
(`--tail N`, `--full`), the counts, the failing tests and the first error line.

Exit 0 means the run is the one expected. Exit 2 means it is not, with the reason: it passed when red was
expected, no test ran, an error came before any assertion, or tests failed. A bug test that awaits
`UnknownCurrency` and meets the raw `HTTPError` is a real red that the runner counts as an error: exit 2,
name that exception in the report and carry on. Exit 1 means the runner could not start, or ran past
`--timeout` (600 s) and had its whole process tree stopped. Before `--suite` it reads free memory, CPU
load and disk space, and drops to one worker under 1.5 GB free or over 85 % CPU.

By hand, the same limits hold. Check memory, CPU and disk first (`Get-CimInstance Win32_OperatingSystem |
Select FreePhysicalMemory`, `(Get-CimInstance Win32_Processor).LoadPercentage`). Run the project's own
command through its package manager (`npm run test`, `pnpm exec vitest run`), never `npx`, which can fetch
a stand-in. Cap the workers (`--maxWorkers=2`, `-j2`), turn watch mode off (`vitest run`,
`jest --watchAll=false`) and lower the priority (`Start-Process -PassThru`, then
`$p.PriorityClass = 'BelowNormal'`).

A watcher, a dev server or a browser started for a test is stopped before the end, and the `node` and
`python` processes are listed to check none of yours is left. A server is ready when its log line
appears: wait on that line with the bounded loop of `systematic-debugging`, never an open-ended sleep. A
test that needs a browser goes through the `chrome-bidi` skill, headless, on its own port.

## Tests after the code

Code written by the user, by another session or found in the history stays, even untested, even when
you are asked to "add tests after". Add the tests one behaviour at a time and prove each one can fail:
break the line it covers on purpose (flip the comparison, return early, drop the call), run the test,
read the red, put the line back with an edit, run it green. The same goes for code you wrote in this
task before its test. The report says these tests came after the code, and how each was proved.

A test written from the stated rule that fails on that code has found a bug, or the rule is wrong. Keep
the test as written. When the user asked you not to touch their code, ask with one `AskUserQuestion`:
fix it ("Corriger (Recommandé)"), or keep the current behaviour and correct the rule. Otherwise fix it
and say so in the report. Untested code you are about to change gets tests for what you touch first,
proved the same way.

## Scratch and commits

A repro script, a scratch file or a fixture made for one run lives in `<temp>/claude-skills/<task>/`,
never in the repository, and is deleted before the end. Nothing named `repro_*`, `scratch_*` or
`debug_*` lands in the repo; the test that stays is the one in the project's test folder.

`clean-commits` takes the work with the exact paths, and the test travels in the same commit as the code
it covers. No `git add .`, no `--no-verify` past a red hook, no commit on a red suite, no push from
here.

## Report

The answer to the user is in French and short. It names the behaviours covered and, for a bug, the
failure line of the test on the unfixed code, then the suite result with every failure named. Tests
written after the code are said to be so, with how each was proved. A question still open is asked
before the last line, never left as a list of things waiting on them.
