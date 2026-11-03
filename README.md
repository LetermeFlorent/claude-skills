# claude-skills

Ten skills for Claude Code and OpenCode, and the commands that start them. Each folder holds the `SKILL.md` the AI reads, a `README.md` for you, and its scripts and tests when it has any. The scripts are plain Python with no dependency, so another AI (Codex, Gemini, Qwen) can use them too: just point it to the `SKILL.md` in its instructions file.

## Install

Ask your AI to follow `INSTALL.md`. It copies the repository into the Claude Code configuration folder, links the skills and copies the commands, without overwriting anything that already has the same name on your machine.

The installation also adds a small check when Claude Code starts. Each time it opens, it looks at the latest version published on GitHub and, if it is newer, installs it: new skills linked, commands updated, removed skills taken out. A copy you have modified and a command you have edited by hand are never overwritten.

Finally it adds a guard before each heavy command (build, tests, docker, node, python...): if memory is too low or the processor or the disk is saturated, the command waits until room frees up, five minutes at most.

## The skills

Each line gives the command that starts the skill and what it does.

| Skill | Command | Role |
|---|---|---|
| strip-ai-traces | `/strip-ai-traces` | writes and fixes text and code without the marks of AI-written text |
| chrome-bidi | `/chrome-bidi` | drives Chrome to open, read, click and capture a page, Windows only |
| clean-code | `/clean-code` | audits and tidies code: short files, one logic per file, dead code |
| clean-commits | `/commit` | splits changes into clean commits, one per intention |
| limited-run | `/limited-run` | starts each task with a memory limit and closes it as soon as it is no longer needed |
| model-effort | `/model-effort` | picks the model and effort level for each agent, never the max effort |
| resource-guard | `/resource-guard` | checks memory, processor and disk before a heavy command, and waits if there is too little |
| stop-resume-agents | `/stop-all`, `/resume-all` | stops everything, subagents included, and resumes later where each one was |
| using-git-worktrees | `/isolate` | isolates a piece of work in a separate working copy |
| writing-skills | `/write-skill` | writes or fixes a skill, and tests it on subagents |

## License

MIT, see `LICENSE`. Copyright (c) 2026 Florent Leterme.
