---
description: Show free RAM, CPU load and disk activity, or wait until there is room before running a heavy command.
argument-hint: "[heavy command to run once there is room]"
allowed-tools: Read,Bash,Skill
---

Arguments: $ARGUMENTS.

Load the `resource-guard` skill and use its `scripts/guard.py`:

- empty: `guard.py check`, and say what is short if anything is;
- a command: `guard.py wait`, then run the command only when it exits 0; on exit 2 say what stayed too high and do not run it.

Short final answer in the user's language: the numbers, and whether the command ran.
