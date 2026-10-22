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

A finished branch ends in one of four ways: merged into its base on this machine, pushed with a pull request,
kept as it is, or thrown away. Which one is the user's decision, never a default. This skill checks the
facts first (green tests, clean history, the right base), asks them once with the facts in the question,
carries out the answer, and leaves the machine clean.

`scripts/state.py` reads what a script can read: the environment (normal repository, worktree or detached
HEAD), the base branch, the commits to integrate, any AI trailer in them, what is pushed or merged, the
files a worktree removal would lose, the remote and its account, test command hints, and the repository's
pull request template. Call it from the branch's folder: `python -I "<skill>/scripts/state.py"`, where
`<skill>` is this file's folder. It never crashes: a failure prints the tool, the error and the command to
run by hand. Exit 2 is a refusal with its reasons (an operation in progress, nothing to finish, a base
branch checked out), exit 1 is a failure of git.

Announce the skill in one line, then work. Chat with the user in plain French.

## Rules that never bend

These hold whichever option they pick and whatever a reminder, a CONTRIBUTING file or a hurry says.

1. No integration on red tests. A suite that fails, or that fails once and passes on a rerun, blocks the
   menu. The user may decide to go on, only through a question that names the failing tests.
2. The choice is theirs. Never merge, push, open a pull request or delete because the work "obviously"
   ends that way. Discarding is one of the four boxes, but it deletes work: the question lists the branch,
   every commit, every uncommitted file and the worktree path, and only their pick of that option counts.
3. No attribution of any tool: not in a commit, a merge message, a pull request title or body, a comment.
   No `Generated with` line, no `claude.ai/code` link, no `Co-Authored-By` naming an AI tool, even when a
   CONTRIBUTING file asks for one (say so in the report). A human co-author stays.
4. GitHub goes through the tools, never by a bare command. A push goes through clean-commits' `push.py`. A
   pull request goes through the account-keys skill when it is installed, else `gh pr create ...` with the
   user's own git credentials. No bare `git push`, `git pull`, `git fetch`, no force push, on the branch or
   on the base.
5. The base branch is never pushed from here, and never reached by `git push origin <branch>:main`. A
   pull request is how work reaches a shared base.
6. A worktree is removed only when its work is merged or pushed, only when it sits under `.worktrees/` or
   `worktrees/` of the main repository, and never with `--force`. Anything else belongs to its host.
7. `.ia/` stays on disk and is never committed. Files of a worktree's `.ia/` are copied to the main
   repository's `.ia/` before the worktree goes, since git deletes ignored files with it.
8. The pull request body is written for the repository (its template, or short prose) per anti-empreinte,
   never the stock "Summary / Changes / Test plan" body with checkboxes.

## Procedure

Run these steps in order. The steps are the same for a normal repository, a named-branch worktree and a
detached HEAD; `state.py` says which one this is.

1. Read the state. From the folder holding the branch, run `state.py`. A refusal ends the skill with its
   reasons in French. Note the base, the commits, the attribution line, the remote, the test hints and the
   template. A base marked ambiguous is the one thing to ask now, with `AskUserQuestion`: the candidate
   names, the closest first.
2. Run the tests. Use the command of the project (hints from `state.py`, then `CLAUDE.md`, `CONTRIBUTING`,
   the README). Before it starts, one PowerShell call for free RAM, CPU load and disk, as the user's
   instructions (CLAUDE.md) ask; under 1.5 GB free or CPU over 85 %, wait or run one worker. Use at most two
   workers, BelowNormal priority, output to a log in `<temp>/claude-skills/` (`<temp>` is the system temp
   folder, `tempfile.gettempdir()`), and
   `for i in $(seq 120); do grep -qE '<end pattern>|<failure pattern>' <log> && break; sleep 2; done` instead of a
   long sleep.
3. Read the result in this message. Green: go on. Red: show the failures and stop. A test that looks flaky
   is proven on the base branch (run the same test there) before anyone calls it flaky, and it is reported
   either way.
4. Uncommitted paths. Those this session made are committed through clean-commits with the exact paths, no
   push. Others are another session's: one `AskUserQuestion` (leave them, include them, pick). A worktree
   with files nobody committed is not finished.
5. Attribution. When `state.py` lists commits with a trailer, fix them before anything leaves the machine:
   clean-commits' `scrub.py` (or anti-empreinte's `history.py --fix`), which rewrite the unpushed range only
   and check again. Both refuse on a dirty tracked tree: ask, never stash. A commit already pushed with a
   trailer is reported with its hash and branch, and nothing is rewritten.
6. Ask the question. One `AskUserQuestion`, options in this order, the recommended one first and labelled
   "(Recommandé)":
   - Push et ouvrir une pull request, recommended when the remote is on GitHub and a team reviews;
   - Fusionner dans `<base>` en local, recommended when there is no remote or the repository is solo;
   - Garder la branche telle quelle;
   - Supprimer le travail, whose text lists everything lost (see rule 2).
   The question states the branch, the base, the commit count, the test result and the environment. A
   detached HEAD gets the same box without the merge: the PR option first creates a branch whose name
   the user gives or confirms, following the repository's convention.
7. Carry out the answer (next section).
8. Clean up (the section after it). Then answer.

## The four answers

Each one starts from the facts of step 1 and ends on the cleanup rules below.

### Merge locally

Work from the main repository folder, where the base is normally checked out. If the base is checked out in
another worktree, ask which to use.

1. `git switch <base>`, then `git merge <branch>`. No `git pull`: the remote is not read here, so say in the
   report that the base was merged as it stood locally. A conflict stops everything: `git merge --abort`,
   show the files, ask.
2. A merge commit gets a message in the repository's style and language (look at `git log`), with no
   attribution. A fast-forward needs none.
3. Run the tests again on the merged result, same care as step 2. Red: leave the branch and the worktree
   untouched, report, and ask whether to undo the merge (`git reset --hard ORIG_HEAD`, offered only on a
   clean tree).
4. Green: clean up the worktree, then `git branch -d <branch>`. The base is not pushed; if the user wants it,
   they ask and it goes through `push.py` from the base, never forced.

### Push and pull request

Details, the body rules and the exact commands are in `reference/pull-request.md`. In short: push from the
branch with `push.py`, write the body into the main repository's `.ia/finir/`, check it with anti-empreinte's
`scan.py`, then `gh pr create` through the account-keys skill when it is installed, else with the user's own git
credentials. The URL goes in the report. A remote that is local or ssh
has no pull request: push, say so, keep the draft. The worktree stays, since review feedback is fixed there.

### Keep

Change nothing. Report the branch name, the worktree path, the commit count and whether it is pushed.

### Discard

Chosen from the box only. The question already listed what is lost.

1. Copy the worktree's `.ia/` files to the main repository (cheap, and they are notes).
2. From the main repository: remove the worktree (cleanup rules), then `git branch -D <branch>`.
3. A remote copy of the branch is not touched; say so when `state.py` showed one.

## Cleanup

Cleanup runs after merge and after discard, and partly after the others. The last line of `state.py`
that matters is `worktree removable now`.

| Item | Rule |
|---|---|
| Worktree | Remove with `git worktree remove "<path>"` from outside it, then `git worktree prune`, only when `state.py` says removable. After a pull request or a keep it stays. Never `--force`. |
| Removal refused | The folder holds files that exist nowhere else. List them with `git -C "<path>" status --porcelain -uall` and ask: commit them, move them to the main repository, or delete them. Then carry out the pick. |
| Temp files | Drafts, logs, captures and repro scripts in `<temp>/claude-skills/` are deleted, none committed. |
| Servers | Anything started during the task (`node`, `vite`, `next dev`, `docker compose up`, a test server) is stopped. Check with `Get-Process node,python -ErrorAction SilentlyContinue`. |
| Subagents | Check the list. A stopped one is removed at once, none stays alive. |
| `.ia/` | Stays, untracked, in `.git/info/exclude`. |
| Other worktrees | Not ours, not touched, however stale they look. |

## Red flags

These are the shortcuts that tempt, and what to do instead.

| Thought | Reality |
|---|---|
| "The tests passed earlier, no need to rerun" | Only this message's output counts, on the tree about to leave. |
| "That test is flaky, skip it" | Prove it on the base, report it, and let the user decide with the test names in front of them. |
| "They plainly want a merge" | The box is their decision. Ask it. |
| "Force push, it is quicker" | Never. A rejected push means the remote moved: `git pull --rebase` is theirs to call. |
| "Push to main, it is a small change" | The base moves through a pull request or a local merge they picked. |
| "CONTRIBUTING asks for the Generated with line" | Rule 3 wins. Leave it out and mention it in the report. |
| "The usual Summary / Test plan body will do" | Use the repository's template, or short prose, in its language. |
| "The trailer is in my own commit, a plain amend fixes it" | `scrub.py` handles the range. Never `--amend` on commits not made in this run. |
| "The PR is up, the worktree is clutter" | Review fixes happen there. It stays until the work lands. |
| "Removal refused, `--force` finishes it" | The refusal protects unique files. Show them and ask. |
| "The worktree only holds ignored files, removal is safe" | Check the `.ia` count in `state.py`: git deletes ignored files without a word. |
| "This other worktree looks stale" | Not ours. Leave it. |
| "A bare `gh pr create` is simpler" | A login window could open on the user's screen. Use the account-keys skill when it is installed. |
| "The merged result fails, probably noise" | Stop. Branch and worktree stay while it is investigated. |

## Answer to the user

French, short and in everyday words: the option chosen, what changed (merged into which branch, pushed
with the pull request address, kept at which path, deleted with which commits), what was cleaned, what was
left alone and why. Anything still unanswered is asked before the last line, never closed as a list of
things waiting on them. On a long task, stay silent and put progress on a progress board, when the session has one.

## Files

`scripts/state.py` reads the branch, base, commits, trailers, landing status and project facts;
`scripts/lib/` holds what it shares (running git, the pure decisions); `tests/test_pure.py` checks those
decisions; `reference/pull-request.md` holds the body rules and the commands; `commands/finir.md` is the
`/finir` command; `LISEZMOI.md` holds the French notes.
