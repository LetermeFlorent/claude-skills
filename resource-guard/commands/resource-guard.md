---
description: Show free RAM, CPU load and disk activity, or wait until there is room before running a heavy command.
argument-hint: "[heavy command to run once there is room]"
allowed-tools: Read,Bash,Skill
---

Arguments: $ARGUMENTS.

Load `resource-guard` skill, use its `scripts/guard.py`:

- empty: `guard.py check`, say what is short if anything;
- a command: one call `guard.py wait && python -I "<limited-run>/scripts/run.py" start -- <command>`, `<limited-run>` = limited-run skill folder, in background when server or watcher; on exit 2 from `guard.py wait` say what stayed too high, command did not run.

Short final answer in user's language: numbers, and whether command ran.
