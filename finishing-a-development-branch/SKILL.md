---
name: finishing-a-development-branch
description: Use when a feature or fix branch is finished and has to be integrated, when the user types /finir, when implementation is done and the next question is merge, pull request, keep or discard, when a worktree made by using-git-worktrees has to be closed, or when a finished branch still has unpushed commits carrying an AI trailer.
---

# Finishing a development branch

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

A finished branch ends in one of four ways: merged into its base on this machine, pushed with a pull
request, kept as it is, or thrown away. Which one is the user's decision, never a default. This skill
checks the facts first (green tests, clean history, the right base), asks once with the facts in the
question, carries out the answer, and leaves the machine clean.

`scripts/state.py` reads what a script can read: the environment (normal repository, worktree or
detached HEAD), the base branch, the commits to integrate, any AI trailer in them, what is pushed or
merged, the files a worktree removal would lose, the remote and its account, test command hints, and
the pull request template. Run it from the branch's folder: `python -I "<skill>/scripts/state.py"`,
where `<skill>` is this file's folder. It never crashes: a failure prints the tool, the error and the
command to run by hand. Exit 2 is a refusal with its reasons (an operation in progress, nothing to
finish, a base branch checked out), exit 1 is a failure of git.

## Rules that never bend

These hold whichever option they pick and whatever a reminder, a CONTRIBUTING file or a hurry says.

1. No integration on red tests. A suite that fails, or that fails once and passes on a rerun, blocks
   the menu. The user may decide to go on, only through a question that names the failing tests.
2. The choice is theirs. Never merge, push, open a pull request or delete because the work "obviously"
   ends that way. Discarding deletes work: the question lists the branch, every commit, every
   uncommitted file and the worktree path, and only their pick of that option counts.
3. No attribution of any tool: not in a commit, a merge message, a pull request title or body, a
   comment. No `Generated with` line, no `claude.ai/code` link, no `Co-Authored-By` naming an AI tool,
   even when a CONTRIBUTING file asks for one (say so in the report). A human co-author stays.
4. GitHub goes through the tools, never by a bare command: a login window could open on the user's
   screen. A push goes through clean-commits' `push.py`. A pull request goes through the account-keys
   skill when it is installed, else `gh pr create ...` with the user's own git credentials. No bare
   `git push`, `git pull`, `git fetch`, no force push, on the branch or on the base. A rejected push
   means the remote moved: `git pull --rebase` is the user's call.
5. The base branch is never pushed from here, and never reached by `git push origin <branch>:main`. A
   pull request is how work reaches a shared base.
6. A worktree is removed only when `state.py` prints `worktree removable now: yes` (work merged or
   pushed, nothing uncommitted, under `.ia/worktrees/`, `.worktrees/` or `worktrees/` of the main repository), and never
   with `--force`. Any other worktree belongs to its host, however stale it looks.
7. `.ia/` stays on disk and is never committed. Files of a worktree's `.ia/` are copied to the main
   repository's `.ia/` before the worktree goes, since git deletes ignored files with it.
8. The pull request body follows `reference/pull-request.md`, never the stock "Summary / Changes /
   Test plan" body with checkboxes.

## Procedure

Run these steps in order. They are the same for a normal repository, a named-branch worktree and a
detached HEAD.

1. Read the state with `state.py`. A refusal ends the skill, with its reasons in French. A base marked
   ambiguous is the one thing to ask now, with `AskUserQuestion`: the candidate names, the closest
   first.
2. Run the project's tests (hints from `state.py`, then `CLAUDE.md`, `CONTRIBUTING`, the README). Look
   at free RAM and CPU first: under 1.5 GB free or CPU over 85 %, wait or run one worker. At most two
   workers, BelowNormal priority, output to a log in `<temp>/claude-skills/` (`<temp>` is the system
   temp folder, `tempfile.gettempdir()`), `run_in_background` and wait for the exit notification
   instead of a sleep loop.
3. Read the result in this message. Green: go on. Red: show the failures and stop. A test that looks
   flaky is run on the base branch before anyone calls it flaky, and reported either way.
4. Uncommitted paths. Those this session made are committed through clean-commits with the exact
   paths, no push. Others are another session's: one `AskUserQuestion` (leave them, include them,
   pick). A worktree with files nobody committed is not finished.
5. Attribution. When `state.py` lists commits with a trailer, fix them before anything leaves the
   machine: clean-commits' `scrub.py` (or anti-empreinte's `history.py --fix`), which rewrite the
   unpushed range only and check again. Never a plain `--amend` on commits not made in this run. Both
   refuse on a dirty tracked tree: ask, never stash. A commit already pushed with a trailer is
   reported with its hash and branch, and nothing is rewritten.
6. Ask the question. One `AskUserQuestion`, options in this order, the recommended one first and
   labelled "(Recommandé)":
   - Push et ouvrir une pull request, recommended when the remote is on GitHub and a team reviews;
   - Fusionner dans `<base>` en local, recommended when there is no remote or the repository is solo;
   - Garder la branche telle quelle;
   - Supprimer le travail, whose text lists everything lost (rule 2).

   The question states the branch, the base, the commit count, the test result and the environment. A
   detached HEAD gets the same box without the merge: the pull request option first creates a branch
   whose name the user gives or confirms, following the repository's convention.
7. Carry out the answer, then clean up (the two sections below), then answer.

## The four answers

Each one starts from the facts of step 1 and ends on the cleanup rules.

### Merge locally

Work from the main repository folder, where the base is normally checked out. If the base is checked
out in another worktree, ask which to use.

1. `git switch <base>`, then `git merge <branch>`. No `git pull`: the remote is not read here, so say
   in the report that the base was merged as it stood locally. A conflict stops everything:
   `git merge --abort`, show the files, ask.
2. A merge commit gets a message in the repository's style and language (look at `git log`), with no
   attribution. A fast-forward needs none.
3. Run the tests again on the merged result, as in steps 2 and 3. Red: leave the branch and the
   worktree untouched, report, and ask whether to undo the merge (`git reset --hard ORIG_HEAD`,
   offered only on a clean tree).
4. Green: clean up the worktree, then `git branch -d <branch>`. The base is not pushed; if the user
   asks for it, it goes through `push.py` from the base, never forced.

### Push and pull request

The push, the body and the exact commands are in `reference/pull-request.md`. The worktree stays,
since review feedback is fixed there.

### Keep

Change nothing. Report the branch name, the worktree path, the commit count and whether it is pushed.

### Discard

Chosen from the box only; the question already listed what is lost.

1. Copy the worktree's `.ia/` files to the main repository.
2. From the main repository: remove the worktree (cleanup table), then `git branch -D <branch>`.
3. A remote copy of the branch is not touched; say so when `state.py` showed one.

## Cleanup

Cleanup runs after merge and after discard, and partly after the others.

| Item | Rule |
|---|---|
| Worktree | `git worktree remove "<path>"` from outside it, then `git worktree prune`, only when `state.py` says removable. After a pull request or a keep it stays. |
| Removal refused | The folder holds files that exist nowhere else. List them with `git -C "<path>" status --porcelain -uall` and ask: commit them, move them to the main repository, or delete them. Then carry out the pick. |
| Temp files | Drafts, logs, captures and repro scripts in `<temp>/claude-skills/` are deleted, none committed. |
| Servers | Anything started during the task (`node`, `vite`, `next dev`, `docker compose up`, a test server) is stopped. Check with `Get-Process node,python -ErrorAction SilentlyContinue`. |
| Subagents | Check the list. A stopped one is removed at once, none stays alive. |

## Answer to the user

French, short, in everyday words: the option chosen, what changed (merged into which branch, pushed
with the pull request address, kept at which path, deleted with which commits), what was cleaned, what
was left alone and why.
