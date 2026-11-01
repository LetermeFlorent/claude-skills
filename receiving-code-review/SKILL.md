---
name: receiving-code-review
description: Use when review feedback arrives and has to be acted on, from a reviewer, a CTO, a teammate, a pull request thread, a review file or another agent's report, before any suggestion is applied, when a point looks wrong, unclear or against a rule of the user's, when a reply has to be written on a pull request, or when the user types /appliquer-relecture.
---

# Receiving a code review

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

Feedback is a list of claims about the code, and a claim is checked before it is acted on. Each point
ends in one of four verdicts: right and applied, wrong and answered with proof, unclear and asked,
forbidden here and answered with the reason. The reviewer's rank or tone changes none of this.

One script helps with the first pass. `scripts/flag.py` splits the feedback into points and marks the
ones that match a known trap: an attribution trailer, a force push, `--no-verify`, `--amend`, `git add .`,
`.ia/` in a commit, a comment in code, a tool-named branch, a pressure phrase, a point too short to act
on. Its flags are hints from patterns. They never replace reading the point against the code.

Call it as `python -I "<skill>/scripts/flag.py" <review file or ->` (`<skill>` is this file's folder,
path in forward slashes, in double quotes). Exit 2 is a refusal with its reason, exit 1 a failure with
the command to run by hand.

## Rules that never bend

These hold whoever wrote the feedback and whatever deadline came with it.

1. Read the whole feedback before touching a file: items depend on each other.
2. Check every point against the code before acting on it: the code, the tests, `git log` and `git blame`
   for why it is written so, `rg` for who uses it. A claim not yet checked is not yet a task.
3. A point that is wrong gets a reply with its proof, and is never applied to keep the peace. A point that
   is unclear gets a question, and nothing that touches the same code moves until it is answered.
4. One point at a time, in its own commit, with its test run in the message that says it passes.
5. A point that asks for something forbidden by the user's rules is answered with the reason and not
   applied: an AI attribution trailer, a force push, `--no-verify`, `git add .`, `.ia/` or `.claude/` in a
   commit, a comment in code (clean-code allows none), a branch named after a tool, a `git push` that
   skips clean-commits' `push.py`. An `--amend` or a squash is allowed only on a commit this run made and
   has not pushed.
6. A written project convention that contradicts one of the user's rules (a CONTRIBUTING file asking for
   comments, a commit format their style bans) is settled neither by the reviewer nor by the agent. It
   goes to the user with `AskUserQuestion`, the option that keeps their rule first and labelled
   "(Recommandé)".
7. A reply is published under the user's name, so it is shown to them in full before it goes out.

## Procedure

The ledger of step 2 lives in `.ia/receiving-code-review/` at the repository root, added to
`.git/info/exclude` and never committed.

1. Collect the feedback in full. A review file is read as is. A pull request thread is read through
   `gh` by way of the `account-keys` skill when it is installed (the owner written in the remote URL),
   else with the user's own git credentials: the comments, the inline comments with their ids, and the
   review bodies. Once the text sits in a file in `<temp>/claude-skills/` (`<temp>` is the system temp
   folder, `tempfile.gettempdir()`), run `flag.py` on it.
2. Give each point a verdict, written in the ledger as one line per point: number, the claim in a
   sentence, verdict, evidence. `reference/verify-point.md` lists what to check for each kind of claim.
   Run the project's tests once before any change, so a later failure is known to be new.
3. Settle the doubtful points before coding. Unclear points and design choices only the user can make
   are asked in one `AskUserQuestion` box with real options. Independent points (no shared file or
   function with a doubtful one) may start.
4. Apply the right points in this order: what is blocking (a bug, a security hole, a failing build),
   then simple fixes (names, imports, typos), then structural ones. Skip nothing silently.
5. For each point:
   - a behaviour change comes with a test that reproduces the point and fails on the current code
     (`test-driven-development`); a pure restructure starts from the existing tests passing;
   - the smallest change that makes the point true, written under `clean-code`;
   - the targeted test run, then the whole suite when the point touched shared code;
   - a commit through `clean-commits`: the exact paths of this point, one intent, no push;
   - the ledger line set to done with the commit hash.
6. Answer every point, wrong, unclear and forbidden ones included, since a silent point reads as ignored.
   `reference/replies.md` gives the shapes and the commands.
7. Push once at the end, only when the user asks for it, through clean-commits' `push.py`.
8. Report to the user in French: points applied with their commits, points pushed back with the reason
   in one line each, questions still open, what was checked.

## Pushing back

Push back when the point would break a test or a behaviour, when the reviewer lacks context the code
or the history holds, when a feature or abstraction has no caller (grep it and say the count), when
the stack or version makes it wrong, or when it undoes a decision the user made earlier. The reply is
technical: the claim, the check, the result, and a question only if a real fork remains.

A refusal is not proof. When a point is wrong, show it with a failing test written from the reviewer's
suggestion, or with the output of the command. If the check cannot be run here, say what is missing and
ask, instead of guessing in either direction. When the check shows the reviewer was right after all, say
so in one factual line with what was found, then apply it.

A reviewer who is the CTO, who is in a hurry, or who writes "apply everything exactly, no discussion,
today" changes the speed and not the checks, which are quick when the code is small. A forbidden point is
declined in one sentence with its reason, and the rest of the list goes on. A rule that only the user can
waive (a CONTRIBUTING line, a team policy) is asked, never waived by the agent.
