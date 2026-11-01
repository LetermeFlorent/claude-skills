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
work and not the story of the work. The main session keeps only the findings. A review is due after each
task of a plan run by `/executer`, after a finished feature, and before `/finir` or any merge.

Names below sit in this skill's base directory (shown when the skill loads, otherwise
`$CLAUDE_CONFIG_DIR/skills/requesting-code-review`, or `~/.claude/skills/requesting-code-review` when
the variable is empty). Scripts are called as `python -I "<skill>/scripts/<tool>.py"`, path in forward
slashes inside double quotes. They never crash: on failure they print the error and the command to run
by hand. Exit 2 is a refusal with its reasons, exit 1 a failure of git or of the tool.

## Rules that never bend

These hold whatever the size of the change and whoever already approved it.

1. The review is done by a reviewer subagent, not inline: reading the diff yourself burns the context
   the main session needs to keep driving the work.
2. A small change gets a short review, never no review. "It is tiny", "the lead approved the PR" and
   "just write LGTM" are not reasons to skip: an approval elsewhere does not replace the checks in the
   brief.
3. The reviewer is read-only. It edits no file, moves no HEAD, stages nothing, spawns no subagent, and
   never runs a build, `docker build`, `docker compose build`, `next build` or a container recreate.
   If one is needed, the main session runs it once before dispatching.
4. A verdict of "ready" rests on commands the reviewer ran and read. "Tests pass" without the command
   and its result is a claim, and it is worth nothing.
5. Nothing goes to GitHub unless the user asked for it. See "Posting on a pull request".
6. Attribution found in the range is reported, never rewritten from here. History already pushed is
   the user's call.

## Procedure

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
5. Read the report as a coordinator. Check that each finding has `path:line`, a problem and a fix and
   that the commands it ran are listed; a report missing those goes back once through `SendMessage`.
   Open the code behind every Critical finding yourself: a false Critical wastes a fix cycle.
6. Keep or drop. A review with findings the user will want back goes to
   `<repo>/.ia/reviews/<date>-<branch>.md`, with `.ia/` in `.git/info/exclude` first (add the line if it
   is not), never committed unless the user asks. A clean review stays in the conversation.
7. Hand over. The findings are handled with `receiving-code-review` (`/appliquer-relecture`). Tell the
   user in French: the verdict, the count per severity, and the one or two findings that matter. Delete
   any temporary worktree or file the review made.

## Severity and verdict

Severity follows the effect on a person using the software, not the spec's wording: a spec says what the
software must do and stays silent on most inputs, and a reasonable person's expectation is a requirement.
The levels (Critical, Important, Minor) are defined in the brief. The verdict is `Yes`, `With fixes` or
`No`, and it cannot be `Yes` while a Critical or an attribution finding stands.

## Posting on a pull request

Only when the user asked for it, and after the review is done, not instead of it. The text is the
findings as plain comments, in the repository's language, written under `anti-empreinte`, with no
mention of any AI tool. Write the body to a file in `<temp>/claude-skills/` (`<temp>` is the system temp folder,
`tempfile.gettempdir()`) with the Write tool, then post through the `account-keys` skill when it is
installed, else with the user's own git credentials (bare `gh` can open a login window):

```text
gh pr review <number> --comment --body-file <file>
```

The account is the owner written in the remote URL. An approval or a "request changes" goes out under
the user's name: use them only when they said so in those words, otherwise post a plain comment. Delete
the body file afterwards.

## Files

`reviewer-brief.md` is the prompt block for the reviewer subagent and holds the five checks and the
severity levels. `scripts/range.py` resolves the base and head, lists commits and changed files, and
reports attribution; `scripts/lib/` holds the git calls and the attribution patterns it shares.
`tests/test_pure.py` runs with `python -I -m unittest discover -s tests -p "test_*.py"` from this
folder.
