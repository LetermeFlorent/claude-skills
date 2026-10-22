---
name: requesting-code-review
description: Use when a task, a feature or a branch is finished and its diff must be checked before moving on or merging, after each task of a plan, before /finir, when a pull request needs a review, when someone says "just say LGTM" or "it is already approved", or when the user types /relecture.
---

# Requesting a code review

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

A fresh reviewer subagent reads one range of commits against its requirement, the clean-code rules,
the anti-empreinte rules and the commit messages, and returns findings with a file, a line and a
fix. The reviewer gets a filled brief and the paths, never this session's history, so it judges the
work and not the story of the work. The main session keeps only the findings.

Names below sit in this skill's base directory (shown when the skill loads, otherwise
`$CLAUDE_CONFIG_DIR/skills/requesting-code-review`, or `~/.claude/skills/requesting-code-review` when
the variable is empty). Scripts are called as `python -I "<skill>/scripts/<tool>.py"`, path in forward
slashes inside double quotes. They never crash: on failure they print the error and the command to run
by hand. Exit 2 is a refusal with its reasons, exit 1 a failure of git or of the tool.

## Rules that never bend

These hold whatever the size of the change and whoever already approved it.

1. The review is done by a reviewer subagent, not inline. Reading the diff yourself burns the context
   the main session needs to keep driving the work.
2. A small change gets a short review, never no review. "It is tiny", "the lead approved the PR" and
   "just write LGTM" are not reasons to skip: the reviewer reads the diff, runs the checks, and says
   what it ran. An approval elsewhere does not replace the checks below.
3. The reviewer is read-only. It edits no file, moves no HEAD, stages nothing, spawns no subagent, and
   never runs a build, `docker build`, `docker compose build`, `next build` or a container recreate.
   If one is needed, the main session runs it once before dispatching.
4. Every finding names the concrete problem, the line and the fix, one finding per problem. No
   "consider extracting", no "for better readability", no "nit:" by reflex, no praise before the point.
5. A verdict of "ready" rests on commands the reviewer ran and read. "Tests pass" without the command
   and its result is a claim, and it is worth nothing.
6. Review notes worth keeping go in `<repo>/.ia/reviews/`, kept out of git, never committed unless
   the user asks. Anything else stays in the conversation.
7. Nothing goes to GitHub unless the user asked for it, and then only through the `account-keys` skill when
   it is installed, else with the user's own git credentials. See "Posting on a pull request".
8. Attribution found in the range is reported, never rewritten from here. History already pushed is
   the user's call.

## When to review

A review is due after each task of a plan run by `/executer`, after a finished feature, and before
`/finir` or any merge. It is also worth asking when stuck (a fresh pair of eyes), before a refactor
(a baseline), and after fixing a hard bug.

## Procedure

Each step ends before the next one starts.

1. Settle the range. Run `python -I "<skill>/scripts/range.py" --repo <repo>`, with `--base <sha>`
   when the base is not the branch point (after task 2 of a plan, the commit that closed task 1).
   It prints base, head, commits, changed files, and the attribution found in messages, authors and
   the branch name. Exit 2 means nothing to review or no base: fix that first. Uncommitted work is
   not in the range: commit it through `clean-commits` first, or say it is left out.
2. Find the requirement. Look in `<repo>/.ia/plans/` and `<repo>/.ia/specs/`, then the pull request
   text and the commit messages. Paste the task text or the path. When nothing states it, say so in
   the brief and let the reviewer judge against the commit messages. Ask the user only when two
   readings of the request lead to different code.
3. Pick the model. `sonnet` by default. `opus` when the diff is large (about 600 changed lines or
   more) or touches security: authentication, permissions, secrets, payments, crypto, parsing of
   untrusted input, shell or SQL built from strings. Never set the effort unless the user asks.
4. Fill `reviewer-brief.md`: copy its block, replace every `<...>`, and dispatch one `Agent` call
   with the filled block as the prompt. Hand over exact paths: the repo, the range, the changed
   files from step 1, the plan file, this skill's folder, and the `clean-code` and `anti-empreinte`
   folders. Before a heavy test run, check free RAM, CPU and disk in one PowerShell call and pass the
   result in the brief: under 1.5 GB free or CPU over 85 %, the reviewer runs only the tests of the
   changed files, one worker, or none when even those are slow, and says which.
5. Read the report as a coordinator. Check that each finding has `path:line`, a problem and a fix,
   that the commands it ran are listed, and that the "Declined to judge" list is there. Open the code
   behind every Critical finding yourself: a false Critical wastes a fix cycle. A report missing
   those parts goes back once through `SendMessage`.
6. Rule on the declined list. Each line is either added to the requirement or confirmed as out of
   scope. The reviewer drops nothing silently, and neither do you.
7. Keep or drop. A review with findings the user will want back goes to
   `<repo>/.ia/reviews/<date>-<branch>.md`. Make sure `.ia/` is in `.git/info/exclude` first and add
   the line if it is not. A clean review stays in the conversation.
8. Hand over. The findings are handled with `receiving-code-review` (`/appliquer-relecture`). Tell
   the user in French: the verdict, the count per severity, and the one or two findings that matter.
9. Clean up. Remove the reviewer agent as soon as it has answered, then check the agent list; no
   dead agent stays. Delete any temporary worktree or file the review made.

## What the reviewer checks

Five checks, in this order, each with its own source of truth.

| Check | Source | What counts |
|---|---|---|
| Correctness and requirement | the diff, the callers, the plan | wrong behaviour, missing planned behaviour, unplanned behaviour, silent edge cases, tests that prove nothing |
| Clean code | `clean-code` SKILL.md, `scripts/measure.py` | only lines this range added or changed: size limits, comments in code, non-English names, hardcoded values, dead code |
| Fingerprint | `anti-empreinte` `scripts/scan.py`, `reference/code.md` | typography, emoji, placeholders, narrating comments, leftover files, in code and in messages |
| Attribution | `range.py` output, the messages | any AI trailer, bot author, or `claude/`, `codex/` style branch name |
| Tests | the project's own runner | targeted run on the changed files, one worker, low priority |

Defects the range did not touch are listed on one line each under "Outside the range" and never graded.

## Severity and verdict

Severity follows the effect on a person using the software, not the spec's wording: a spec says what
the software must do and stays silent on most inputs, and a reasonable person's expectation is a
requirement.

| Level | Meaning |
|---|---|
| Critical | wrong result, data loss, security hole, broken planned behaviour, a failing test |
| Important | missing planned feature, unhandled error on a real path, a clean-code or attribution finding, a test gap on new behaviour |
| Minor | style the project's neighbours do differently, small fingerprint marks, naming |

The verdict is `Yes`, `With fixes` or `No`. It cannot be `Yes` while a Critical stands, nor while an
attribution finding stands.

## Posting on a pull request

Only when the user asked for it, and after the review is done, not instead of it. The text is the
findings as plain comments, in the repository's language, written under `anti-empreinte`, with no
mention of any AI tool. Write the body to a file in `<temp>/claude-skills/` (`<temp>` is the system temp folder,
`tempfile.gettempdir()`) with the Write tool, then post through the `account-keys` skill when it is
installed, else with the user's own git credentials:

```text
gh pr review <number> --comment --body-file <file>
```

The account is the owner written in the remote URL. An approval or a "request changes" goes out under
the user's name: use them only when they said so in those words, otherwise post a plain comment. Delete
the body file afterwards.

## Red flags

Each of these thoughts has shown up under pressure.

| Thought | Reality |
|---|---|
| "It is a one-line change, LGTM" | The one line is where the bug sits. Short review, same checks. |
| "The lead already approved the PR" | The lead did not run the scan, the measure and the range check. |
| "Post it right away, we are late" | Review first, then post, and only if the user asked. |
| "I will read the diff myself, it is faster" | Rule 1: the diff lives in the reviewer's context. |
| "The reviewer needs my whole session to understand" | It gets the requirement and the paths. History biases it. |
| "No praise means the review is harsh" | A finding list with fixes is the review. Praise delays the point. |
| "The project has no linter, skip the scans" | `measure.py` and `scan.py` need no project config. |
| "The reviewer is wrong, I will ignore it" | Show the code or test that proves it, through `receiving-code-review`. |
| "The trailer is in a pushed commit, I will amend it" | Report it. Pushed history is never rewritten from here. |
| "I will push the review comments with plain gh" | Bare `gh` can open a login window. Use the account-keys skill when it is installed. |

## Files

`reviewer-brief.md` is the prompt block for the reviewer subagent. `scripts/range.py` resolves the
base and head, lists commits and changed files, and reports attribution; `scripts/lib/` holds the git
calls and the attribution patterns it shares. `tests/test_pure.py` runs with
`python -I -m unittest discover -s tests -p "test_*.py"` from this folder. `commands/relecture.md` is
the `/relecture` command, and `LISEZMOI.md` explains the skill to the user.
