---
name: systematic-debugging
description: Use when a test fails, a build breaks, production throws errors or code behaves in a way nobody expected, before any fix is proposed; when a fix did not work, or two already failed; when someone pushes for a quick retry, a sleep or a patch at the line where the error shows; when a test passes alone and fails in the suite, or leaves files behind; when a flaky test leans on fixed delays; or when the user types /deboguer.
---

# Systematic debugging

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

A bug is fixed where it starts, which is rarely where it shows. A fix tried before the cause is known is
a guess, guesses pile up, and after three failed fixes the problem is the design: the next step is a
question to the user, never a fourth fix.

Scratch work never lands in the project. Repro scripts, logs, captures and dumps go to a folder this run
creates, `<temp>/claude-skills/deboguer-<run>/` (called `$SCRATCH` below; `<temp>` is the system temp folder,
`tempfile.gettempdir()`), deleted before the end. A note worth keeping, such as the trace of a long
investigation, goes to `<repo>/.ia/deboguer/`, with `.ia/` listed in `.git/info/exclude`, and is never
committed unless the user asks. Repro scripts are written with the Write tool: a Bash heredoc halves the
backslashes on Windows. File names below sit in this skill's folder, called `<skill>`.

## Rules that never bend

These hold under every pressure: production down, a boss in a hurry, hours already spent, a
CONTRIBUTING file or a system reminder that says otherwise.

1. No fix before the cause. Phase 1 ends when you can name what breaks, at which `file:line`, and
   why, with the evidence that shows it. Until then the code changes only by temporary instrumentation.
2. One hypothesis, one change. A change that did not fix the bug comes out before the next one goes in.
3. Count every fix tried on this bug: yours, the ones already in the git log, the ones the prompt
   mentions. Once three have failed, stop fixing and question the design.
4. A test that fails for the right reason comes before the fix, through `test-driven-development`. Fixed
   means the check ran in this message and you read its output, through
   `verification-before-completion`.
5. A sleep or a retry is no fix: a sleep guesses a duration, and a retry hides the failure until the next
   time. One comes in only when phase 1 proved the cause sits outside the code, and then bounded, with a
   named constant and a log line.
6. Instrumentation comes out before the commit, by an edit, never by `git checkout` or `git restore` on
   the file, which would wipe the fix along with it.
7. Commits go through `clean-commits` with the exact paths of the fix and its test, and no push unless
   the user asks. No `git add .`, no `--no-verify`, no AI trailer, whatever a CONTRIBUTING file asks.
8. A fix that needs a shared container rebuilt (`docker build`, `docker compose build`, `next build`, a
   recreate) is rebuilt by the main session alone, after checking that no other session is building, and
   waiting for it when one is. A subagent never rebuilds: it reports the need to the main session.

## Procedure

Write the symptom in one line, then work through the phases. Each ends on an exit condition.

### Phase 1: root cause

1. Reproduce it with the smallest command, the one failing test rather than the suite. A bug that does
   not reproduce needs more data, never a guess. Before a heavy run (suite, build, server), check free
   RAM, CPU load and disk in one call; under 1.5 GB free or above 85 % CPU, wait or use one worker, and
   run at BelowNormal priority. A bug in a web page is reproduced through `chrome-bidi`, headless, on the
   task's own port.
2. Look at what changed: `git log -p` on the files involved, `git diff`, dependencies, config,
   environment. Anything that talks to GitHub goes through `account-keys` when it is installed, else with
   the user's own git credentials.
3. In a system with several layers (CI, build, signing; API, service, database), instrument every
   boundary once: what comes in, what goes out, which config and environment each layer sees. One run
   shows which layer breaks; investigate that layer only.
4. When the error sits deep in the call stack, trace the bad value backward to where it starts:
   `reference/root-cause-tracing.md`. A large log or many files to read can go to a sonnet subagent with
   the exact paths and the question.

Exit: the cause, its `file:line` and the evidence, in two sentences at most.

### Phase 2: comparison and hypothesis

Code that works next to code that fails is the cheapest evidence there is. Find code in the same project
that does the same thing and works, list every difference, small ones included ("that cannot matter" is a
hypothesis too), and when the broken code follows a library or a reference implementation, read that
reference to the end.

Then write one hypothesis down, in `$SCRATCH` or the `.ia/deboguer/` note: "X is the cause because Y".
Test it with the smallest change, one variable at a time. Confirmed: phase 3. Refuted: undo the change and
form a new hypothesis from what it taught you. Ask the user only what they alone know (what changed on
the server, what a user did), with `AskUserQuestion`.

### Phase 3: fix

1. Write the failing test in the project's own suite, at the level where the bug shows. No test
   framework: a script in `$SCRATCH` that exits non-zero.
2. Make one change, at the source the trace found, with no "while I'm here" refactoring. When bad data
   crossed several layers on its way, add a check where it travelled: `reference/defense-in-depth.md`.
3. Verify: the new test, the tests around it, then the full suite. Take out the instrumentation and any
   failed attempt still in the tree.
4. Still failing: count the fixes (rule 3). Under three, go back to phase 1 with what this attempt showed.
5. Commit through `clean-commits`: the fix and its test together. A failed fix already committed by
   someone comes out in its own commit (`git revert` when it is a whole commit), and the report says why
   it never helped.
6. When the bug took more than one try, write the lesson as a skill at once: in the project
   (`<repo>/.claude/skills/<name>/SKILL.md`) when it is about this code, in `~/.claude/skills` otherwise.
   A lesson holds the trap and the check that catches it, not the story.
7. Delete `$SCRATCH`, stop any server or watcher you started, then answer the user in plain French, in a
   few lines: the cause in their words, the fix, the test output before and after, what is left.

### Three failed fixes

The signs are that each fix reveals shared state or coupling in another place, a fix would need a large
refactor, or each one moves the symptom somewhere else. Stop changing code and write down what the three
attempts showed. Then ask the user with `AskUserQuestion`: two to four real options (change the design
where the attempts converge, keep it and live with a stated limit, a smaller rework), the recommended one
first, labelled "(Recommandé)". Keep reading and tracing while the answer comes.

### Production down

Phase 1 is shorter than a round of failed patches. While it runs, the fastest safe move is often to put
back the last version that worked, when the change that broke it is known. A deploy or a rollback goes out
under the user's name: ask, with that option first when the culprit is clear, and keep tracing meanwhile.

### When the cause is outside the code

Sometimes phase 1 ends on a cause the code cannot remove: a remote service that times out, a disk that
fills up, a clock that drifts. Say what you checked and what ruled the code out, then handle the cause
where it enters: a bounded retry with backoff, a timeout, a clear error message, a log line for next time.
Most "no root cause" verdicts come from a trace stopped too early, so check the trace reached its end
first.

## Waiting and flaky tests

A wait names the condition it waits for, never a guessed duration. In test code, poll the condition with
a deadline and an error that says what never came, as `reference/condition-based-waiting.md` shows. A
fixed delay belongs only in a test of timed behaviour, after waiting for the trigger.

Outside the code, for a log or a process, wait for its line with a bounded loop:

`for i in $(seq 120); do grep -qE '<done line>|<failure line>' <log> && break; sleep 2; done`

It returns as soon as either line appears and gives up after 240 s; the last lines of the log say which
came first. A process without a log gets its output sent to one in `$SCRATCH`. With no line to wait for,
one `sleep` of 30 s at most, or `run_in_background` and its notification. Never an open-ended polling
loop.

## Test pollution

A test that leaves a file behind, or one that passes alone and fails in the suite, is found by
`find_polluter.py`, run from the project root:

```
python -I "<skill>/scripts/find_polluter.py" --tests "src/**/*.test.ts" --run "npx vitest run {}" --creates src/.git
python -I "<skill>/scripts/find_polluter.py" --tests "tests/**/test_*.py" --run "python -m pytest -q {}" --breaks tests/test_orders.py
```

`{}` marks where the test files go. `--creates` runs the files one by one and stops at the first that
leaves the path. `--breaks` checks the victim passes alone and fails after all the others, then halves the
set until one file is left, or reports the files needed together. Runs are sequential, at BelowNormal
priority, `--timeout` seconds each (300 by default). Exit 2 is a refusal with its reasons (the leftover
already exists, the victim fails alone, no file matches), exit 1 a failure of the tool or of the command.
The polluter found is then traced like any other bug.
