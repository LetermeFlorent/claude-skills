# claude-skills

Twelve skills for Claude Code and OpenCode, and the commands that start them. Each folder holds the `SKILL.md` the AI reads, a `README.md` for you, and its scripts and tests when it has any. The scripts are plain Python with no dependency, so another AI (Codex, Gemini, Qwen) can use them too: just point it to the `SKILL.md` in its instructions file.

## Install

Ask your AI to follow `INSTALL.md`. It copies the repository into the Claude Code configuration folder, links the skills and copies the commands, without overwriting anything that already has the same name on your machine.

The installation also adds a small check when Claude Code starts. Each time it opens, it looks at the latest version published on GitHub, and those of Ponytail and graphify, and installs whatever is newer: new skills linked, commands updated, removed skills taken out. A copy you have modified and a command you have edited by hand are never overwritten.

It also adds a guard before each heavy command (build, tests, docker, node, python...): if memory is too low or the processor or the disk is saturated, the command waits until room frees up, five minutes at most.

## The skills

Each line gives the command that starts the skill and what it does.

| Skill | Command | Role |
|---|---|---|
| strip-ai-traces | `/strip-ai-traces` | writes and fixes text and code without the marks of AI-written text |
| browser-bidi | `/browser-bidi` | drives Chrome, or Firefox on request, to open, read, click and capture a page, Windows only |
| clean-code | `/clean-code` | audits and tidies code: short files, one logic per file, dead code |
| drive-project | `/drive` | takes a goal to pushed commits: every question first, then a silent run that shows only a percentage, every task handed to helper agents |
| clean-commits | `/commit` | splits changes into clean commits, one per intention |
| limited-run | `/limited-run` | starts each task with a memory limit and closes it as soon as it is no longer needed |
| claude-model-effort | `/claude-model-effort` | picks the Claude model and effort level for each agent, never the max effort |
| other-model-effort | `/other-model-effort` | the same choice for models that are not Claude, in light, all-round and top tiers |
| resource-guard | `/resource-guard` | checks memory, processor and disk before a heavy command, and waits if there is too little |
| stop-resume-agents | `/stop-all`, `/resume-all` | stops everything, subagents included, and resumes later where each one was |
| using-git-worktrees | `/isolate` | isolates a piece of work in a separate working copy |
| writing-skills | `/write-skill` | writes or fixes a skill, and tests it on subagents |

## Tools that come with it

Three outside tools are installed and kept at their latest release with the skills, without any plugin.

| Tool | Command | Role |
|---|---|---|
| [Ponytail](https://github.com/DietrichGebert/ponytail) | `/ponytail`, `/ponytail-review`, `/ponytail-audit` | makes the agent write the smallest change that fully works, always on at its highest level (ultra) |
| [graphify](https://github.com/Graphify-Labs/graphify) | `/graphify` | turns a large codebase into a knowledge graph to query, used on large projects only |
| [caveman](https://github.com/JuliusBrussee/caveman) | none, the agents are picked by the AI | its cavecrew agents and caveman-explore find, edit and review code and answer in very short reports, used on small projects |

## License

MIT, see `LICENSE`. Copyright (c) 2026 Florent Leterme.
