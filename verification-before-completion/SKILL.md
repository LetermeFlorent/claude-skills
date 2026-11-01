---
name: verification-before-completion
description: Use when about to say that work is done, fixed, passing, built, committed or pushed, before a commit or a PR, when a subagent, a colleague or an earlier message reports success, when someone says the tests take too long or to trust the report, or when the user types /verifier, with or without a claim, a file or a task to check.
---

# Verification before completion

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

A claim of success is worth the command that was run for it, in the same message, and the output that
was read. Memory of an earlier run, a confident feeling, a green linter standing in for a build and a
subagent's "done" are guesses. The wording does not matter: "fixed", "should work", "all good" and a
silence that lets the reader assume success are all claims.

## Rules that never bend

These hold before any statement about the state of the work.

1. No claim without a fresh check. It runs in this message, completely, and its output is read to the
   end: exit code, count of failures, the lines that matter. A run from before the last edit proves
   nothing about the code after it.
2. A failure is reported with its output: the failing line, the claim it breaks, no softening. A skipped
   step (missing tool, no network, too heavy for now) is named and the claim stays open.
3. A verified result is stated plainly, "34 tests pass" with the command, and no hedging word next to it.
4. A partial check proves its part. One test file proves that file, a linter proves style, a type check
   proves types. Say "the 3 tests of this module pass" until the full run is done.
5. Someone else's "done" is not evidence: a subagent, a script's final line, an earlier session, a
   CONTRIBUTING file or a reminder that says not to rerun the tests. Read the diff or run the check.
6. Pressure (a deadline, a long suite, an authority saying to trust the report) shrinks the check to a
   targeted run. It never removes it.

## Procedure

Name the claim in one line, run the command that would fail if the claim were false (table below),
read all of the output, then state the claim with the evidence or the real status with the output. With
`/verifier` the claim is the argument. Without one, list the claims the session made or implied and check
each.

## What proves what

The middle column is the evidence a claim needs, the right column is what people use instead.

| Claim | Needs | Does not prove it |
|---|---|---|
| Build succeeds | the build command, exit 0 | the linter, a log that looks fine |
| Bug fixed | the original symptom replayed and gone | a changed line, a passing unrelated test |
| Regression test valid | red then green: it fails without the fix, passes with it | a test that passed once |
| Subagent finished | its diff or its output, read | its own report |
| Requirements met | the request re-read line by line | tests passing |
| Commit made | `git log -1 --stat` and `git status --short`: right paths, right message, nothing else staged | the commit command not erroring |
| Push done | what `push.py` printed, with the refused or accepted line | "no error appeared" |
| Page or screen looks right | a screenshot read through chrome-bidi | the code that should produce it |
| File written clean | `python -I "<anti-empreinte>/scripts/scan.py" <path> --no-git` with no row left | rereading it by eye |
| Code written clean | the clean-code `scripts/measure.py` run on the touched files, no finding | a feeling it is tidy |

## Checks on this machine

Resources. Before a test suite, a build, docker or a dev server, one PowerShell call reads free RAM,
CPU load and disk (`Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory`,
`(Get-CimInstance Win32_Processor).LoadPercentage`,
`Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"`). Under 1.5 GB free or CPU over 85 %, do not
stack: wait, or use one worker. Start with a targeted run, then the full one when the claim is about the
whole project. At most 2 workers (`--maxWorkers=2`, `-j2`), at BelowNormal priority. A server started
for the check is stopped before the end. Wait on a line with
`for i in $(seq 120); do grep -qE '<done line>|<failure line>' <log> && break; sleep 2; done`,
never on a duration. A subagent never runs `docker build`, `next build` or a container recreate; the
main session does it once.

Visual results. A page, a layout, a colour or an animation is checked with a screenshot through the
chrome-bidi skill (`/test-visuel`), on its own debugging port and profile. Never Playwright, never the
user's own Chrome. The screenshot is read, not just taken, and a capture already looked at is not
looked at twice.

## Reporting

The final answer is short, in the user's language and in everyday words: the claim, the command that
was run, what the output showed, in that order.
