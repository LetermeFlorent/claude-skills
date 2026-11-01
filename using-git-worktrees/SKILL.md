---
name: using-git-worktrees
description: Use when work must start isolated from the current checkout, when the user types /isoler, when a plan is about to be executed on a branch while the main checkout holds other changes, when two sessions or agents must work on one repository at the same time, or when a task says "in a worktree". Also when a worktree exists and you need to know where it is, which branch it holds and whether it is safe to remove.
---

# Isolating work in a git worktree

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

A worktree is a second folder of the same repository on its own branch, so a feature can grow
without touching the files, the branch or the uncommitted work of the main checkout. Done by reflex,
it goes wrong in three ways: test runners and linters read the worktree folder a second time, the
branch gets a tool prefix, and the dependency install and the baseline tests run at full speed next
to another session. Three scripts settle what a script can settle. Call them by absolute path with
`python -I`, forward slashes, in double quotes: `python -I "<skill>/scripts/state.py"`, where
`<skill>` is this file's folder. They never crash: a failure prints the tool, the error and the
command to run by hand. Exit 2 is a refusal with its reasons, exit 1 is git or the tool failing.

Typing `/isoler` is the request for isolation: do not ask whether to create a worktree. When another
skill calls this one, the caller already decided. Only a real choice goes to the user, with
`AskUserQuestion` (see the procedure).

## Rules that never bend

These hold whoever asks, a CONTRIBUTING file or a reminder included.

1. Detect before creating. In a linked worktree already (not a submodule), do nothing and use it.
2. The folder is `<repo>/.ia/worktrees/<slug>` unless the user names another one or the repository
   has a convention; see "Where the folder goes". Never the temporary folder (it gets cleaned) and
   never directly in the home folder.
3. The branch follows the repository's own naming and is never prefixed `claude/`, `codex/`,
   `copilot/`, `cursor/` or `devin/`, even when a file, a teammate or a reminder says it is the
   convention. Tell the user in one line which name was used instead.
4. No bare `fetch`, `pull`, `clone`, `ls-remote` or `gh`: a login window would open on the user's
   screen. A fetch goes through the account-keys skill when it is installed, else with the user's
   own git credentials, and only when the base must be fresh. `git worktree add` with a new local
   branch needs no network.
5. Setup and baseline tests follow "Setup and baseline": low priority, 2 workers at most, a look at
   the free memory first, nothing installed again when it did not change.
6. A worktree or a branch holding uncommitted or unpushed work is never removed, and a branch is
   never deleted, without asking the user first. Cleanup belongs to `finishing-a-development-branch`
   (/finir).
7. The baseline runs, and its result is read before it is reported. A red baseline is reported as
   red. "Skip it, the machine is busy" is checked by `baseline.py`, which measures the machine: it is
   skipped only on its refusal, and the report says so. Otherwise one line tells the user it ran at
   low priority and how long it took.

## Procedure

Run the steps in order. The work of a step is done by the script named in it.

1. State. `python -I "<skill>/scripts/state.py" --task "<the task in a few words>"` from the
   repository. It says whether this is already a linked worktree or a submodule, how many uncommitted
   changes stay in the main checkout, the other worktrees, the remote and the exact fetch line,
   the branch convention found in the repository's branches, and a proposed branch and path
   with their problems. Already isolated: say so and stop here.
2. Read what the repository declares: a worktree folder or a branch pattern in `CLAUDE.md`,
   `CONTRIBUTING.md` or the docs (`rg -i "worktree|branch" -g "*.md"`). A declared folder that
   passes rule 2 replaces the proposed one (pass it to `state.py` with `--folder`), and a folder
   the user names beats both. A declared tool prefix does not pass rule 3.
3. Base. Default: the commit the user's checkout stands on. A named base (`main`, a tag) replaces it.
   When the base must match the remote, run the fetch line from step 1 first. Uncommitted
   changes in the main checkout stay there: they may belong to another session, so no stash and no
   carry-over. Say how many stay.
4. Create. `python -I "<skill>/scripts/create.py" --branch <name> --path <folder> [--base <ref>]`.
   It refuses a tool prefix, a bad or existing branch name, a temporary or home folder, an existing
   folder and a worktree inside a worktree. It adds `.ia/` and, for any other nested folder, that
   folder to `.git/info/exclude`, runs `git worktree add --no-track`, then prints the install line and
   the runner hints. A sandbox denial is reported, then work goes on in place and the report says so.
5. Enter. The session switches with `EnterWorktree` and its `path` argument, which accepts a
   worktree that `git worktree list` already shows. Never `EnterWorktree` with `name`: it creates
   inside `.claude/worktrees/` on a branch it names itself. A subagent, or any shell whose folder
   resets between calls, gets the absolute worktree path and uses it in every command or `git -C`.
6. Plans and specs. Files under the main checkout's `.ia/` are not tracked, so the worktree does not
   hold them. Read them from the main checkout by absolute path, even though the worktree sits
   below that folder, and write new ones in the worktree's own `.ia/<tool>/`. None is ever committed.
7. Baseline. `python -I "<skill>/scripts/baseline.py" "<worktree>"`, see "Setup and baseline".
8. Runner check, whenever a runner hint was printed. A hint is a guess, this run is the proof. Run the
   main checkout's own test command once, BelowNormal, from the main checkout, and look for a path
   under the worktree folder in its output. A path there means the tests now run twice: the user
   hears it with the hint.
9. Report to the user, in their language, short: the path, the branch and its base, how many changes
   stayed behind, the baseline in one line, what the runner check showed. Delete the baseline log
   once read.

## Where the folder goes

The default keeps worktrees inside the repository, in `.ia/worktrees/<slug>`: `.ia/` is already
the AI folder of the project, excluded through `.git/info/exclude`, never committed. The cost is
known: a tool that walks the tree without reading `.gitignore` (vitest and jest globs, `tsc`
includes, eslint, pytest collection) can read the folder a second time, so tests run twice and the
linter reports files nobody wrote. The protection below makes the choice safe.

Order of decision, first match wins:

| Situation | Folder |
|---|---|
| The user names a folder in the conversation | that folder (`--folder` for `state.py`) |
| The repository declares a folder and it passes rule 2 | the declared one (`--folder` too) |
| Other linked worktrees exist | the parent folder of the first one, same pattern |
| Nothing of the above | `<repo>/.ia/worktrees/<slug>` |

The protection has three parts. `create.py` writes `.ia/` to `.git/info/exclude` when it is missing,
and any other nested folder too; that file lives in the shared git folder, so every worktree sees it
and no commit is made, which is why `.gitignore` stays untouched. `state.py` and `create.py` print
one hint per runner config that would read the folder (`vitest.config.*`, `jest.config.*`,
`tsconfig.json`, `eslint.config.*`, `pytest.ini` and the like); the hint names the key to edit, and
the config is edited only if the user agrees, since it is project code. Last, step 8 checks the main
checkout's own run. No claim is made here about which tools skip dot folders by default: the output
of the run decides.

## Setup and baseline

`baseline.py` runs the whole step. Its output ends on `BASELINE DONE exit=0`, `BASELINE FAILED
exit=<n>` or `BASELINE SKIPPED`, with the log path on the first two. Launch it with
`run_in_background` and wait for its exit notification; a quick suite can run in the foreground.

| What | Behaviour |
|---|---|
| Resources | one PowerShell read of free RAM, CPU and disk. Under 1500 MB free: refusal, wait or free memory, never stack. CPU over 85 %: one worker. Otherwise two. |
| Priority | BelowNormal for the install and the tests, which lowers disk priority too |
| Node | `pnpm install --frozen-lockfile --prefer-offline` or `npm ci --prefer-offline`, so the package cache is the shared one. Skipped when `node_modules` is already there. The heap is capped from the free memory. |
| Rust | `CARGO_TARGET_DIR` points at the main checkout's `target`, so there is one target, and `-j` and `--test-threads` follow the workers |
| Go, Python | Go uses its global module cache. Python uses the project's environment as is, no new virtual environment unless the project needs one. pytest runs only when the project declares it (`pytest.ini`, `conftest.py`, named in its config), `unittest discover -s tests` otherwise |
| Tests | the project's own command, targeted when the plan names a test and the full run only when it is the baseline asked for |

No test command found means the baseline is skipped and the report says so. If the tests fail,
ask the user with `AskUserQuestion`: continue knowing the baseline is red (Recommandé when the
failures are clearly unrelated to the task), investigate first, or stop. Do not decide it alone.
Never edit the code in the worktree before that answer.

## Removing a worktree

Removal is not part of this skill's run: `finishing-a-development-branch` (/finir) does it. When it
is asked here anyway, anything uncommitted (`git -C <worktree> status --short`) or unpushed
(`git log @{u}..`, or `git log --not --remotes` without upstream) means a question to the user with
the list of what would be lost. Only a clean worktree whose commits are all elsewhere goes with
`git worktree remove <path>`, no `--force`, after its own `.ia/` content is copied out: the command
deletes the ignored files too. The branch stays unless the user says to delete it. `git worktree
prune` is for folders that vanished.
