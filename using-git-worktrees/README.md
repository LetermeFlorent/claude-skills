# using-git-worktrees

A skill and a command to open an isolated workspace (a git worktree) before starting a feature. To install it, see `INSTALL.md` at the root of the repository.

## /isolate

Type `/isolate` when a task must start without touching your folder, its branch or the files not yet committed. Claude checks that it is not already in a worktree, picks a branch and a folder, creates the worktree, then runs the starting tests. It does not ask whether you want a worktree: the command is the request. An argument gives the task (`/isolate cart with discount`) and, if needed, the starting branch (`/isolate discount on the develop branch`).

By default the worktree goes in `<repo>/.ia/worktrees/<task>`, a folder excluded from git without touching `.gitignore`. A folder you name, or that the repository declares, comes first. Never the temp folder or the home folder. Vitest, jest, tsc, eslint or pytest may read this folder a second time: Claude shows the config line that would keep them out and only changes it if you agree.

The branch follows the repository's naming and never carries a tool prefix (`claude/`, `codex/`, `copilot/`, `cursor/`, `devin/`). No bare `git fetch`: it would open a login window. Files that are modified but not committed stay in your original folder.

## The starting tests

Claude first measures memory, processor and disk. Under 1.5 GB free it waits, otherwise it runs the install and the tests at low priority, with two workers at most. If the tests fail, it lets you choose: carry on, look first, or stop.

## Removing a worktree

Only when you ask. A worktree or a branch that holds uncommitted or unpushed work is never removed without your agreement.

## What is in the folder

`SKILL.md` holds the procedure. `scripts` has `state.py` (reads the repository, suggests a branch and a folder), `create.py` (checks then creates) and `baseline.py` (resources, install, tests), with their shared parts in `scripts/lib`. `tests/test_pure.py` covers the pure parts.
