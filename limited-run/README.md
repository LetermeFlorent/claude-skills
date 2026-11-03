# limited-run

Several agents work at the same time on the same PC. Every program they start (development server, file watcher, tests, build) takes memory and processor time from the others, and a forgotten server keeps running for hours. This skill teaches the agent to start each program with a memory limit and a low priority, to write it down, then to stop it as soon as it is no longer needed. To install it, see `INSTALL.md` at the root of the repository.

## /limited-run

Type `/limited-run` followed by a command to start it with a memory limit. `/limited-run list` shows what is running, `/limited-run stop --all` stops everything. With nothing after it, the agent takes stock and stops what is no longer needed.

## What the agent does

It goes through `scripts/run.py start -- <command>` for everything it starts. By default the limit is half of the free memory, between 512 and 4096 MB. On Windows, it covers the program and everything it starts in turn, and if the launcher dies, everything stops with it. On Linux and macOS, it applies to each program separately.

When the result is there (the page shows up, the tests have passed), it stops the task. Before handing back, it prints the list of tasks still running with `run.py list` and stops them with `run.py stop`. It never touches a program it did not start itself with this tool: it may belong to another session.

## Other agents

Claude Code reads the skill by itself. For Codex CLI, Gemini CLI or Qwen Code, add one line to their instructions file (`AGENTS.md`, `GEMINI.md`, `QWEN.md`) that points to `SKILL.md`. The sentence to copy is in `SKILL.md`.

## What is in the folder

`SKILL.md` holds the rules. `scripts/run.py` starts, lists and stops tasks, with its parts in `scripts/lib`. `tests/test_pure.py` checks the calculations and starts real programs on the machine: exit code, memory limit exceeded, low priority, stopping the whole process tree.
