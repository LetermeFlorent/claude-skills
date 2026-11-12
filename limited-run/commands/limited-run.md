---
description: Start a command with a memory cap and low priority, list the tasks started that way, or stop them.
argument-hint: "[command to start | list | stop <name or pid> | stop --all]"
allowed-tools: Read,Bash,Skill
---

Arguments: $ARGUMENTS.

Load the `limited-run` skill and use its `scripts/run.py`:

- a command: `run.py start -- <command>`, in the background when it is a server or a watcher;
- `list`, `stop <name or pid>`, `stop --all`: pass them on as they are;
- empty: `run.py list`, then stop each listed task this session started whose result is already in hand, and keep the others: the list holds every session's tasks.

Short final answer in the user's language: what started with its cap, or what is running and what was stopped.
