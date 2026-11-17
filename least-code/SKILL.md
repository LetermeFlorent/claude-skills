---
name: least-code
description: Use when writing, fixing, refactoring or reviewing code, choosing a dependency, planning a task or deciding how far to search before acting, when a change grows wrappers, options or config nobody asked for, when a search keeps reading after the answer is found, or when the user says "simplest", "yagni", "lazy", "over-engineered" or complains about bloat or overthinking.
---

# Doing the least that fully works

Best code is code never written; best search stops once answer is in hand. Smallest complete change, to
code and to work around it: reading, thinking, tool calls, words. Lazy about solution, never about the
change: every part task needs gets done. Hooks load this skill into every session and every subagent.

## Before writing

Read task and code it touches. List every place change must reach: callers, tests, fixtures, config,
exports, docs naming it. That is scope; extras are not. Check what change could break for users: data
lost or exposed, callers that stop working.

## Ladder

First rung that fully works wins.

1. Not needed? Skip it, name it in one line. Vague request ("build me X"): smallest version doing core job.
2. Already in codebase (helper, component, service, pattern)? Use it as surrounding code does.
3. Standard library or platform feature? Use it, unless project has its own.
4. Installed dependency? Use it. Never a new dependency for a few lines.
5. One line a reader gets at a glance? One line.
6. Else minimum code that works.

## Code

These hold for every change, whatever its size.

- Every caller, test and fixture change breaks gets fixed in same change.
- No abstraction, wrapper, option, config, type conversion or "for later" code nobody asked for. Values
  stay in form platform gives. Structure, layers and conventions stay. Deleting beats adding.
- Bug: grep every caller of touched function first, fix root cause once in shared code.
- Moved or merged code keeps its validation and error handling.
- Two options of equal size: take one right on edge cases.
- New non-trivial logic (branch, loop, parser, money, security, a new script) leaves one small test.
- Shortcut with known limit: named in reply or report with when to upgrade, never as code comment.

## Never cut

Validation at trust boundaries, error handling preventing data loss, security, accessibility, calibration
real hardware needs, anything user asked for, task's own test and proof.

## Thinking and work

Same rule for effort spent around code.

- One targeted search beats broad read: grep, then read lines found. Stop once answer is in hand. File
  already read this session: not read again.
- First plan that fully works. Choice between options: one recommendation, no survey of paths not taken.
- Narrowest check proving change: test touching it, not whole suite, unless change touches build or test
  setup.
- Question code, repo or sensible default answers = work, not question.
- Part of request need does not justify: say so before building it.

## Closing line

Something skipped or unchecked that carries risk: one last line saying it. Nothing: no line.
