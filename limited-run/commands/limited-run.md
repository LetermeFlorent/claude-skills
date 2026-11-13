---
description: Start a command with a memory cap and low priority, list the tasks started that way, or stop them.
argument-hint: "[command to start | list | stop <name or pid> | stop --all]"
allowed-tools: Read,Bash,Skill
---

Arguments: $ARGUMENTS.

Load `limited-run` skill, use its `scripts/run.py`:

- a command: `run.py start -- <command>`, in background when server or watcher;
- `list`, `stop <name or pid>`, `stop --all`: pass on as is;
- empty: `run.py list`, then stop each listed task this session started whose result is in hand, keep others: list holds every session's tasks.

Short final answer in user's language: what started with its cap, or what runs and what was stopped.
