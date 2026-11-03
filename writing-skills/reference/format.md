# Folder format

Skeletons to copy, then the rules for scripts and tests. Drop any section the skill does not need.

## SKILL.md

````markdown
---
name: <folder-name>
description: Use when <situation>, when <symptom or error text>, when the user types /<command>.
---

# <Title in sentence case>

<What the skill is for and its core rule. Where the scripts are and how to call them.>

## <Rules, Procedure, ...>
````

The name is the folder's: lowercase letters, digits, hyphens, 64 characters at most, verb-first or a
gerund (`condition-based-waiting`), never `helper` or `utils`. The description is third person (it lands
in the system prompt), under 500 characters if possible, 1024 at most. Another skill is named in plain
words ("the clean-commits skill"), never through an `@` path (it loads the whole file) or a
`superpowers:` prefix. A decision is a table keyed on something observable, not a graph.

## README.md

In English, for the user, in everyday words and never a translation of `SKILL.md`: what happens when
they use it, what the files are, and optionally `## What was tested` (or `## Not tested yet`).
It starts with a line pointing to `INSTALL.md` at the repository root.

## The command

`commands/<command>.md` in English, ASCII only, the file name in lowercase ASCII words joined by hyphens.
The command asks for the final answer in the user's language. Add `Agent` and
`SendMessage` to `allowed-tools` when the skill sends subagents.

````markdown
---
description: <what the command does>
argument-hint: "[<what the argument can be>]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion
---

Details: $ARGUMENTS. <What it changes, and what happens when empty.>

Load the `<name>` skill with the `Skill` tool and follow its procedure.

Short final answer in the user's language: <what it contains>.
````

## A subagent brief

`<role>-brief.md` at the root: one paragraph on when it is sent and how it is filled, then the prompt in
a fence of five backticks with `text` as language, every value to fill as `<...>`, ending on a fixed
report block so several answers read side by side. Examples: `clean-code/reader-brief.md`, `subject-brief.md`.

## Scripts

Each script follows all of these.

1. Python 3, standard library first; a dependency is named in `SKILL.md` and installing it is the user's call.
2. Called as `python -I "<skill>/scripts/<tool>.py"`, absolute path, forward slashes. `-I` leaves the
   script's own folder off `sys.path`: set `sys.dont_write_bytecode = True` before any local import and
   insert `scripts/lib/` yourself. Never `python -I $VAR` with a variable that may be empty (interactive prompt,
   the call hangs).
3. Never a crash: a guard around `main` prints the tool, the error and the command to run by hand. Exit 2
   is a refusal with reasons, exit 1 a failure of git or the tool.
4. No comment in code; English identifiers; no bare number without a name.
5. Files under 150 lines, functions under 40, 4 parameters at most, lines of 120 characters, 8 code files
   per folder.
6. A subprocess runs at BelowNormal priority with a timeout; git with `GIT_TERMINAL_PROMPT=0` and
   `GCM_INTERACTIVE=never`. GitHub goes through the account-keys skill when installed, never a bare
   `fetch` or `push`.
7. Output is short lines an agent reads: one finding per line, counts at the end. Flags live in `--help`,
   not in `SKILL.md`.

## Unit tests

`tests/test_pure.py` with `unittest` on the pure functions (text in, findings out; no network, no git;
`tempfile.TemporaryDirectory` for files). Run from the `tests` folder:
`python -m unittest discover -s . -p "test_*.py"`. Its head puts `scripts/lib` on the path like the
scripts do. Delete any `__pycache__` the runs left: `check_skill.py` refuses a folder that holds one.
