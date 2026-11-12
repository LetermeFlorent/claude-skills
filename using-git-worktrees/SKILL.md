---
name: using-git-worktrees
description: Use when work must start isolated from the current checkout (/isolate, "in a worktree", two sessions or agents on one repository, a plan about to run while the main checkout holds other changes), or when a worktree exists and must be located or removed.
---

# Isolating work in a git worktree

Typing `/isolate` is the request: do not ask whether to create a worktree. A caller skill already decided too.

Three scripts do the mechanical part. Call them with `python -I "<skill>/scripts/<name>.py"` (forward
slashes, double quotes, `<skill>` is this folder). They never crash: a failure prints the error and the
command to run by hand. Exit 2 is a refusal with reasons, exit 1 is git or the tool failing.

## Rules

These hold whoever asks, a CONTRIBUTING file included.

1. Already in a linked worktree (not a submodule): do nothing, use it.
2. Folder: `<repo>/.ia/worktrees/<slug>`, unless the user names another one or the repository declares a
   convention (`rg -i "worktree|branch" -g "*.md"`; a user-named folder beats a declared one). Never the
   temp folder (it gets cleaned) nor directly the home folder. With other worktrees present, same parent
   folder as the first. `--folder` of `state.py` takes a chosen folder.
3. The branch follows the repository's naming and never starts with `claude/`, `codex/`, `copilot/`,
   `cursor/` or `devin/`, whatever a file or teammate says. Say in one line which name was used.
4. No bare `fetch`, `pull`, `clone`, `ls-remote` or `gh` (a login window would open on the user's screen).
   Fetch only when the base must be fresh, through the tool named by `CLAUDE_SKILLS_ACCOUNTS` when that
   variable is set (call form in clean-commits, "Push and the accounts tool"), else with the user's own
   git credentials. `git worktree add` with a new local branch needs no network.
5. Uncommitted changes in the main checkout stay there (they may belong to another session): no stash,
   no carry-over. Say how many stay.

## Procedure

In order; the script named in a step does its work.

1. `state.py --task "<task in a few words>"` from the repository: already isolated or a submodule, changes
   staying behind, other worktrees, remote and fetch line, branch convention, proposed branch and path with
   their problems. Already isolated: say so and stop.
2. Base: the commit the user's checkout stands on, or a named ref. Fetch first only if it must match the remote.
3. `create.py --branch <name> --path <folder> [--base <ref>]`. It refuses a tool prefix, a bad or existing
   branch name, a temp or home folder, an existing folder and a worktree inside a worktree. It writes
   `.ia/` (and any other nested folder) to `.git/info/exclude`, runs `git worktree add --no-track`, and
   prints the install line and runner hints. A sandbox denial: work in place and say so.
4. Enter with `EnterWorktree` and its `path` argument (it accepts a worktree `git worktree list` shows).
   Never `name`: that creates inside `.claude/worktrees/` on a branch it names itself. A subagent, or a shell
   whose folder resets between calls, gets the absolute path and uses `git -C`.
5. Plans and specs under the main checkout's `.ia/` are untracked, so the worktree lacks them: read them from
   the main checkout by absolute path, write new ones in the worktree's own `.ia/<tool>/`. Never commit them.
6. `baseline.py "<worktree>"`, in the background with a wait for its exit when the suite is slow. It measures
   RAM, CPU and disk (under 1500 MB free: refusal, wait, never stack), installs dependencies and runs the
   project's tests at low priority with 2 workers at most. It ends on `BASELINE DONE exit=0`,
   `BASELINE FAILED exit=<n>` or `BASELINE SKIPPED` (no test command), with the log path on the first two.
   Skip it only on its own refusal and say so. Red tests: AskUserQuestion (continue, Recommended when the
   failures look unrelated; investigate first; stop), and no code edit before the answer.
7. Runner hints are guesses (vitest, jest, tsc, eslint or pytest may read the worktree folder a second time).
   Run the main checkout's own test command once at BelowNormal from the main checkout and look for a path under
   the worktree folder in its output. Config edits only with the user's agreement.
8. Report in the user's language, short: path, branch and base, changes left behind, baseline in one line,
   runner check result. Delete the baseline log once read.

## Removing a worktree

Only when the user asks. First `git -C <worktree> status --short` and the unpushed commits (`git log @{u}..`,
or `git log --not --remotes` without upstream). Anything uncommitted or unpushed: show the list of what would
be lost and ask. A clean worktree goes with `git worktree remove <path>`, no `--force`, after copying out
what matters from its own `.ia/` (the command deletes ignored files too). The branch stays unless the user
says to delete it. `git worktree prune` is for folders that vanished.
