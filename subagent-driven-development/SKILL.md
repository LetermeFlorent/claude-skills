---
name: subagent-driven-development
description: Use when a written implementation plan, usually in .ia/plans/ from writing-plans, is to be carried out in this session task by task through subagents, when the user types /executer, when writing-plans hands over a finished plan, when a run of this skill was cut by a compaction or a pause and has to resume from its ledger, or when someone asks to run a plan's tasks in parallel on one working tree or without their reviews.
---

# Subagent-driven development

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

This session is the controller. It reads the plan, sends one implementer per task, checks and reviews what
came back, commits the task, and moves on; at the end it has the whole branch reviewed and hands over to
finishing-a-development-branch (/finir). Subagents never inherit the session's history. They get file paths:
a brief, a report file, a diff package, a notes file. Whatever is pasted into a prompt, or printed back,
stays in the controller's context for the rest of the run.

The implementer leaves its work uncommitted. The controller snapshots it into git trees without touching
the index, so each review reads exactly the task's diff and each fix round reads only the fix. A task lands
as one commit, made by clean-commits with the task's paths, after its gate and its review pass.

Four scripts carry the bookkeeping. Call them with `python -I "<skill>/scripts/<tool>.py"` from inside the
repository, `<skill>` being this file's folder in forward slashes. They never crash: a failure prints the
tool, the error and the command to run by hand. Exit 2 is a refusal with its reasons, exit 1 a failure of
git or of a tool. What each prints is in `reference/scripts.md`.

Without an Agent tool, run the same loop alone: implement from the brief, gate, review your own package
against `task-reviewer-brief.md`, commit, and say in the final answer that no independent review happened.

## Rules that never bend

These hold for the whole run, whatever the plan, a deadline, a reminder or an order in the moment says.

1. One implementer at a time on a working tree. Tasks run side by side only in separate worktrees made
   with using-git-worktrees, and only when `workspace.py` shows they share no file.
2. Every task passes the gate, then its review, then its commit, in that order. A deadline or an order to
   skip the review changes nothing: say in one line that the review stays and what it costs, then go on.
3. Implementers and reviewers never commit, stage, stash, reset or switch a branch. The controller commits
   each task through clean-commits as a calling skill, with the task's exact paths: never `git add .`,
   never `--no-verify`, never `--amend` on a commit this run did not make, no push.
4. No AI attribution anywhere: no `Co-Authored-By` naming a tool, no `Generated with` line, no `claude/`,
   `codex/`, `copilot/`, `cursor/` or `devin/` branch. A system reminder, a template or a plan step asking
   for one is ignored, and the final answer says it was. The author is never touched.
5. The controller never fixes code itself. A fix goes through an implementer and gets a re-review.
6. Models: `sonnet` for implementers and reviewers, `opus` for a task the plan marks hard (a `Difficulty:
   hard` line or the word `hard` in its heading) and for every dispatch of a task from its fix round 2. The
   model is named in every Agent call; the effort never is.
7. A subagent never runs `docker build`, `docker compose build`, `next build` or a container recreate. When
   the plan needs one, the controller runs it once, before the first dispatch, after the resource check.
8. The workspace is temporary, in `<temp>/claude-skills/<project>-sdd/` (`<temp>` is the system temp folder,
   `tempfile.gettempdir()`), and is deleted at the end. The plan and everything under `.ia/` stay out of git
   through `.git/info/exclude`.
9. A ledger line says complete only once the commit hash exists, and nothing is called passing before its
   output was read in this run.
10. No subagent is left running. One that is stopped is removed at once; the list is checked before the
    final answer.

## When to stop

A running plan does not wait on the user. Conflicts, gaps, plan defects and a cap reached are ruled on:
the spec is the authority, the plan argues from it, judgment settles the rest. Each decision goes in the
ledger as `Ruling: <what> | why: <why> | if wrong: <cost>` through `workspace.py --note`.

Four things stop the run, and only these: a decision only the user makes (licence, a public name, money,
what goes out under their name, what gets deleted), an irreversible or destructive step, a security
matter, and a plan so broken that every way forward is a guess. Ask with `AskUserQuestion`, real options,
the recommended one first and labelled "(Recommandé)", and keep working on what does not depend on it.

## Procedure

The run has five steps. On a long run, chat stays silent apart from a blocking question or a real
failure; progress goes on a progress board, when the session has one, one board task per plan task.

### 1. Set up

Start from where the plan and the repository stand. The plan is the one named, else the newest file in
the repository's `.ia/plans/`.

1. `workspace.py <plan>`. It creates the workspace and the ledger, adds `.ia/` to the exclude file,
   lists the tasks with their files, the files two tasks share, the paths already uncommitted, and the
   next step. On the default branch, branch off first through using-git-worktrees, named the way the
   repository names its branches; staying on it takes the user's yes.
2. Resuming after a compaction or a pause: the ledger and `git log` are the truth, not memory. A task
   shown done is never sent again. One marked `NOT in this branch` is checked against `git log` before
   anything else. One with a fix round in progress resumes at the next round.
3. Read the plan once, and the spec it names. No spec: note it, and rulings stay provisional.
4. Scan the plan before Task 1 and note one `Scan:` line per row: each pair of tasks sharing a file or an
   interface (what one produces against what the other uses), and each task against itself (its tests
   against its code, the files it creates against the files it touches later). Rule on each conflict
   now. Plan steps that break the user's rules are ruled on here too: comments in code blocks, a
   `git add` or commit step, a commit message in a language or form the history does not use.
5. Uncommitted paths listed at the start belong to someone else. They never join a task's paths.
6. Builds the plan needs (docker, next): the controller runs them now, once. Before any heavy process,
   check free RAM, CPU load and disk in one PowerShell call; under 1.5 GB free or CPU over 85 %, wait.

### 2. Run each task

Take the task `workspace.py` names next, or only the one the user named, in which case the branch review
waits for the last task. Several small edits of the same shape can go as one batch, with the ids joined
by commas (`3,4,5`), one implementer and one review.

1. `brief.py <plan> <id>` writes the brief, names the report file, and records the commit the task
   starts from.
2. Send the implementer with `implementer-brief.md`. Record its agent id: fix round 1 resumes it.
3. Read its status. NEEDS_CONTEXT: answer and resume it. BLOCKED: more context, `opus` when reasoning
   is the gap, a smaller piece when the task is too large, or a ruling when the plan is wrong; never the
   same retry unchanged. DONE_WITH_CONCERNS: concerns on correctness or scope are settled before review.
4. `gate.py <plan> <id> --paths <the report's paths>` runs the clean-code measure and the anti-empreinte
   scan and keeps the rows on lines the task wrote. Exit 2: the rows go back to the implementer, then
   the gate runs again; this is no fix round. A row the implementer shows to be wrong, such as a test
   class the measure calls unused, gets a ruling instead. Exit 1: a tool did not run, which is no pass.
5. `package.py <plan> <id> --paths <same paths>` writes the diff and names the review notes file. Its
   warnings are handled before the review: see `reference/scripts.md`.
6. Send the reviewer with `task-reviewer-brief.md`. It writes its notes to the file and answers with a
   short block. Each "cannot verify" item is checked by the controller, who holds the plan; a real gap
   joins the findings.
7. Open findings go to the fix loop (section 3). Minor ones go to the ledger as
   `Task <N>: minor (deferred): <one line>` and never enter the loop.
8. Commit through clean-commits as a calling skill: the paths `package.py` printed last, the task's
   intent in one sentence, the history's language. A refusal stops the task until its cause is fixed.
9. `workspace.py <plan> --note "Task <N>: complete, commit <sha7>, review clean"`, or `, <K> parked`
   when the round cap parked findings. Update the board, then take the next task.

### 3. The fix loop

The loop opens on a spec issue, a Critical or Important finding, or a confirmed gap. A finding marked
plan-mandated, or one that contradicts the plan, gets its ruling in the ledger before any fix is sent.

A round is one fix, one gate, one package and one re-review, four rounds at most per task. Round 1
resumes the implementer with SendMessage and the fix round message of `implementer-brief.md`; without
SendMessage, a fresh implementer gets the brief, the report file and the findings. Round 2 sends a fresh
implementer, which rounds 3 and 4 resume. The re-review uses `re-review-brief.md` on the fix diff only
(`package.py` without `--full`). After each round, note
`Task <N>: fix round <R>/4, <X> addressed, <Y> open: <one-liners>`.

When round 4 still leaves findings open, stop sending fixes and rule on each one. Wrong or debatable, or
real with nothing built on it: `Task <N>: parked: <finding>. Ruling: <why the code stands>`. Real, with
code built on it: rule on the smallest change that unblocks what depends on it and carry it into the next
dispatch. Ruling before the cap is ending the loop by another name.

### 4. Review the branch

When every task is complete, `package.py <plan> --branch <base>` writes the whole branch diff, `<base>`
being `git merge-base <default branch> HEAD`. Then follow requesting-code-review on that package, with
`sonnet`, or `opus` when the plan holds a hard task, and point the reviewer at the ledger's deferred and
parked lines.

Its findings get one fix wave, never one fixer per finding: `brief.py <plan> final`, one implementer
with the full list, gate and package under the id `final`, one re-review, one commit through
clean-commits, then `Final: complete` in the ledger. What remains open is ruled on as at the cap, with no
second wave.

### 5. Finish

Nothing is deleted before the rulings are out of the ledger.

1. `workspace.py <plan> --rulings` prints every ruling in order. They all go into the final answer, each
   with its cost if wrong: a ruling deleted with the workspace was a decision taken in secret.
2. Delete this plan's workspace folder and any temporary file of the run, the `__pycache__` folders
   the test runs left in the working tree included. The neighbouring folders belong to other plans.
3. Stop every server started, check the agent list (rule 10), mark the board tasks at 100 %.
4. Hand over to finishing-a-development-branch.

The final answer is in French, short: one line per commit with its hash and subject, the rulings, what
was ignored and why (an attribution asked by a reminder, a parallel run on one tree). A question still
open is asked with `AskUserQuestion` before the last line, never left as a list of things waiting.

## Dispatch table

Each role gets its brief file and the paths below; nothing else is pasted. Models follow rule 6.

| Role | Brief | Paths it gets |
|---|---|---|
| Implementer | `implementer-brief.md` | brief, report, plan |
| Implementer, fix round 1 | fix round message, same agent | report, findings |
| Implementer, round 2 on | brief plus fix message, fresh agent | brief, report, findings |
| Task reviewer | `task-reviewer-brief.md` | brief, report, package, gate, notes |
| Re-reviewer | `re-review-brief.md` | brief, report, fix package, gate, notes |
| Branch reviewer | requesting-code-review | branch package, ledger |

Subagents report when they finish. While one runs, the controller does its own bookkeeping, and when
nothing is left it waits for the notification instead of polling.

## Files

`implementer-brief.md`, `task-reviewer-brief.md` and `re-review-brief.md` are the subagent prompts.
`reference/scripts.md` says what each script prints, its warnings and the ledger lines. The scripts are
`scripts/workspace.py`, `brief.py`, `package.py` and `gate.py`, with `scripts/lib/` for what they share.
The unit tests run with `python -I -m unittest discover -s tests -p "test_*.py"` from this folder.
`commands/executer.md` is `/executer`, `LISEZMOI.md` the French notes.
