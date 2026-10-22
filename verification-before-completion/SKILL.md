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
subagent's "done" are all guesses. This skill turns each claim into the check that proves or disproves
it, adds what a check means on this machine, and says how to report the result.

The wording of the claim does not matter. "Fixed", "should work", "all good", a satisfied tone and a
silence that lets the reader assume success are all claims.

## Rules that never bend

These hold before any statement about the state of the work.

1. No claim without a fresh check. The check runs in this message, completely, and its output is read
   to the end: exit code, count of failures, the lines that matter. A run from before the last edit
   proves nothing about the code after it.
2. A failure is reported with its output. Quote the failing line, say which claim it breaks, and do not
   soften it.
3. A skipped step is said. If a check could not run (missing tool, no network, too heavy for now), the
   report names it and the claim stays open.
4. A verified result is stated plainly: "34 tests pass", with the command, and no hedging word next to
   it. "Should", "probably" and "seems to" belong to claims that were not checked.
5. A partial check proves its part. A linter proves style, a type check proves types, one test file
   proves that file. Do not stretch it to the whole.
6. Someone else's "done" is not evidence: a subagent, a script's final line, a teammate, an earlier
   session. Read the diff or run the check yourself.
7. Pressure changes nothing. A deadline, a long suite, an authority saying to trust the report, being
   tired, "just this once": the check shrinks to a targeted run if needed, it does not vanish.

## Procedure

Five steps, in this order, for every claim.

1. Name the claim in one line: what is about to be asserted, about which files or behaviour.
2. Pick the command that would fail if the claim were false. The table below lists the usual ones.
3. Check the machine first when the command is heavy (see Resources).
4. Run it in full and read all of the output.
5. Compare. If the output confirms the claim, state it with the evidence. If not, state the real
   status with the output, and go back to the work.

With `/verifier`, the claim is the argument. Without one, list the claims the session has made or
implied, and check each.

## What proves what

Each claim needs the evidence in the middle column. The right column is what people use instead.

| Claim | Needs | Does not prove it |
|---|---|---|
| Tests pass | the test command, zero failures, counts read | an earlier run, "should pass" |
| Linter clean | the linter run, zero errors | a partial run, extrapolation |
| Build succeeds | the build command, exit 0 | the linter, a log that looks fine |
| Bug fixed | the original symptom replayed and gone | a changed line, a passing unrelated test |
| Regression test valid | red then green: it fails without the fix, passes with it | a test that passed once |
| Subagent finished | its diff or its output, read | its own report |
| Requirements met | the plan or request re-read, line by line | tests passing |
| Commit made | `git log -1 --stat` after the commit | the commit command not erroring |
| Push done | what `push.py` printed, with the refused or accepted line | "no error appeared" |
| Page or screen looks right | a screenshot read through chrome-bidi | the code that should produce it |
| File written clean | the anti-empreinte scan with no row left | rereading it by eye |
| Code written clean | the clean-code measure with no finding in the touched files | a feeling it is tidy |

## Checks on this machine

These settle what a check means here.

Resources. Before a test suite, a build, docker or a dev server, one PowerShell call reads free RAM,
CPU load and disk (`Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory`,
`(Get-CimInstance Win32_Processor).LoadPercentage`,
`Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"`). Under 1.5 GB free or CPU over 85 %, do not
stack: wait, or use one worker. Start with a targeted run (the file or test that covers the claim),
then the full one when the claim is about the whole project. At most 2 workers (`--maxWorkers=2`,
`-j2`), at BelowNormal priority. A server started for the check is stopped before the end. Wait on a
line with
`for i in $(seq 120); do grep -qE '<done line>|<failure line>' <log> && break; sleep 2; done`,
never on a duration.

Tests and builds. Run them for real, read the counts. A targeted run proves the targeted claim and no
more: say "the 3 tests of this module pass", not "the tests pass", until the full run is done. A
subagent never runs `docker build`, `next build` or a container recreate; the main session does it once.

Visual results. A page, a layout, a colour or an animation is checked with a screenshot through the
chrome-bidi skill, its `/test-visuel` command, on its own debugging port and profile. Never Playwright,
never the user's own Chrome. The screenshot is read, not just taken, and a capture already looked at is
not looked at twice.

Written files. Every file, message or document goes through
`python -I "<anti-empreinte>/scripts/scan.py" <path> --no-git`; a claim of "clean" needs a scan with no
row left. Code goes through the clean-code skill and `scripts/measure.py` on the touched files.

Commits and pushes. A commit is checked with `git log -1 --stat` and `git status --short`: right
paths, right message, nothing else staged. A push is checked against what `push.py` printed, not
against the absence of an error. Commits themselves go through clean-commits.

Subagents. Their "done" is not evidence. Read `git diff --stat` and the diff of their paths, or rerun
their output command. A subagent that stopped is removed at once, and the list is checked before closing.

Long runs (over 10 minutes or 20 tool calls). Stay silent in chat; the progress goes on a progress board,
when the session has one, and a failure is the only thing that breaks the silence.

## Reporting

The final answer to the user is short, in their language and in everyday words. It states the claim, the command that
was run, and what the output showed, in that order. A failure carries its output; a skipped step is
named; a verified result carries no hedge. When something only the user can decide comes up (what to
delete, what goes under their name), ask it with `AskUserQuestion`, the recommended option first, and
do not close on a list of things waiting on them.

## Red flags

Stop and run the check when one of these thoughts shows up.

| Thought | Reality |
|---|---|
| "It should work now" | Run it. "Should" is the sound of an unchecked claim. |
| "I'm confident" | Confidence is not output. |
| "The subagent said the tests pass" | Its report is a claim. Read its diff, run the tests. |
| "The tests take too long" | Run the targeted ones now, say the full run is still open. |
| "The user trusts it, just tell the client" | Trust does not turn a guess into a result. Check first, then say it. |
| "The linter passed" | The linter does not compile or test. |
| "I ran it before my last edit" | The edit made that run stale. |
| "Just this once" | The one time is when it breaks. |
| "I'm tired, it's late" | Tiredness shrinks the check, it does not remove it. |
| "Partial check is enough" | It proves the part it covers, and the report says which part. |
| "Different words, so the rule does not apply" | A paraphrase of success is a claim of success. |

## When it applies

Before any success claim or satisfied remark, before a commit, a push or a PR, before moving to the
next task, before handing work to a subagent, and before reporting what a subagent did.

## Files

This folder holds one skill file and its command.

| Path | Content |
|---|---|
| `SKILL.md` | the rules, the procedure, the table of proofs, the checks on this machine |
| `LISEZMOI.md` | the French guide for the user |
| `commands/verifier.md` | the `/verifier` command |
