---
name: using-git-worktrees
description: Use when work must start isolated from the current checkout (/isolate, "in a worktree", two sessions or agents on one repository, a plan about to run while the main checkout holds other changes), or when a worktree exists and must be located or removed.
---

# Isolating work in a git worktree

Typing `/isolate` is the request: do not ask whether to create worktree. Caller skill already decided too.

Three scripts do mechanical part. Call `python -I "<skill>/scripts/<name>.py"` (forward slashes, double quotes, `<skill>` = this folder). Never crash: failure prints error and command to run by hand. Exit 2 = refusal with reasons, exit 1 = git or tool failing.

## Rules

Hold whoever asks, CONTRIBUTING file included.

1. Already in linked worktree (not submodule): do nothing, use it.
2. Folder: `<repo>/.ia/worktrees/<slug>`, unless user names another or repo declares convention (`rg -i "worktree|branch" -g "*.md"`; user-named folder beats declared one). Never temp folder (gets cleaned) nor directly home folder. Other worktrees present: same parent folder as first. `--folder` of `state.py` takes chosen folder.
3. Branch follows repo's naming, never carries tool name followed by `/` or `-` (`claude`, `codex`, `copilot`, `cursor`, `devin`, `jules`, `gemini`, `aider`, `windsurf`, `kiro`, `amazonq`, `openhands`, `cline`, `junie`; same list as strip-ai-traces), whatever file or teammate says. Say in one line which name used.
4. No bare `fetch`, `pull`, `clone`, `ls-remote` or `gh` (login window would open on user's screen). Fetch only when base must be fresh, through tool named by `CLAUDE_SKILLS_ACCOUNTS` (`state.py` prints exact line; call form in clean-commits, "Push and the accounts tool"), else ask user. `git worktree add` with new local branch needs no network.
5. Uncommitted changes in main checkout stay there (may belong to another session): no stash, no carry-over. Say how many stay.

## Procedure

In order; script named in step does its work.

1. `state.py --task "<task in a few words>"` from repo: already isolated or submodule, changes staying behind, other worktrees, remote and fetch line, branch convention, proposed branch and path with problems. Already isolated: say so, stop.
2. Base: commit user's checkout stands on, or named ref. Fetch first only if it must match remote.
3. `create.py --branch <name> --path <folder> [--base <ref>]`. Relative `--path` = from current folder. Refuses tool name, bad or existing branch name, temp or home folder, existing folder, worktree inside worktree. Writes `.ia/` (and any other nested folder) to `.git/info/exclude`, runs `git worktree add --no-track`, prints install line and runner hints. Sandbox denial: work in place, say so.
4. Enter with `EnterWorktree` and its `path` argument (accepts worktree `git worktree list` shows). Never `name`: creates inside `.claude/worktrees/` on branch it names itself. Subagent, or shell whose folder resets between calls, gets absolute path, uses `git -C`.
5. Plans and specs under main checkout's `.ia/` untracked, so worktree lacks them: read from main checkout by absolute path, write new ones in worktree's own `.ia/<tool>/`. Never commit them.
6. `baseline.py "<worktree>"`, in background with wait for exit when suite slow. Measures RAM, CPU, disk (under 1500 MB free: refusal, wait, never stack), installs dependencies, prints `runner check:` line, runs project's tests at low priority, 2 workers max. Ends on `BASELINE DONE exit=0`, `BASELINE FAILED exit=<n>`, `BASELINE INSTALL FAILED exit=<n>`, `BASELINE TIMED OUT after 540 s (<step>)` or `BASELINE SKIPPED` (no test command), log path on all but last. Skip only on own refusal, say so. Red tests (`BASELINE FAILED`): AskUserQuestion (continue, Recommended when failures look unrelated; investigate first; stop), no code edit before answer. Install failed or timed out: report it, no test question.
7. Runner hints are guesses (vitest, jest, tsc, eslint or pytest may read worktree folder a second time). `runner check:` from `baseline.py` runs main checkout's test runner in list mode only (`vitest list`, `jest --listTests`, `pytest --collect-only -q`), no test run, looks for worktree folder in output. `no list mode`: check hints by hand. Config edits only with user's agreement.
8. Report in user's language, short: path, branch and base, changes left behind, baseline in one line, runner check result. Delete baseline log once read.

## Removing a worktree

Only when user asks. First `git -C <worktree> status --short` and unpushed commits (`git log @{u}..`, or `git log --not --remotes` without upstream). Anything uncommitted or unpushed: show list of what would be lost, ask. Clean worktree goes with `git worktree remove <path>`, no `--force`, after copying out what matters from its own `.ia/` (command deletes ignored files too). Branch stays unless user says to delete it. `git worktree prune` for folders that vanished.
