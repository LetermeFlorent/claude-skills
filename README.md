# claude-skills

Seventeen skills for Claude Code and OpenCode, and the commands that start them. Each folder holds the `SKILL.md` the AI reads, a `README.md` for you, and its scripts and tests when it has any. The scripts are plain Python with no dependency, so another AI (Codex, Gemini, Qwen) can use them too: just point it to the `SKILL.md` in its instructions file.

## Install

Ask your AI to follow `INSTALL.md`. It copies the repository into the Claude Code configuration folder, links the skills and copies the commands, without overwriting anything that already has the same name on your machine.

The installation also adds a small check when Claude Code starts. At most once every six hours, it looks at the latest version published on GitHub and installs it if it is newer: new skills linked, commands updated, removed skills taken out. A copy you have modified and a command you have edited by hand are never overwritten. It says nothing when everything is up to date.

Two more hooks give every session, and every subagent a session starts, the rules of the terse-speech and least-code skills at the very beginning, so they are followed without anyone asking. If a skill file is missing, it is skipped and nothing breaks.

Earlier versions also installed three outside tools: Ponytail, caveman and graphify. They are gone from the installer, and the next update removes what they left on your machine: their links, copied agents and commands, downloaded copies, hooks and the graphify package. Anything you changed by hand is left in place and reported.

It also starts the progress-board page, a small local server at http://127.0.0.1:8790, and sets it to start at every login (on Windows, through the `Run` key of your user account).

It also adds a guard before each heavy command (build, tests, docker, node, python...): if memory is too low or the processor or the disk is saturated, the command waits until room frees up, five minutes at most.

## The skills

Each line gives the command that starts the skill and what it does.

| Skill | Command | Role |
|---|---|---|
| strip-ai-traces | `/strip-ai-traces` | writes and fixes text and code without the marks of AI-written text |
| browser-bidi | `/browser-bidi` | drives Chrome, or Firefox on request, to open, read, click and capture a page, Windows only |
| clean-code | `/clean-code` | audits and tidies code: short files, one logic per file, dead code |
| clean-architecture | `/clean-arch` | audits and reorganises the folder tree: misplaced, duplicated and useless files, crowded folders, cycles |
| drive-project | `/drive` | takes a goal to pushed commits: every question first, then a silent run that shows only a percentage, every task handed to helper agents |
| clean-commits | `/commit` | splits changes into clean commits, one per intention |
| limited-run | `/limited-run` | starts each task with a memory limit and closes it as soon as it is no longer needed |
| claude-model-effort | `/claude-model-effort` | picks the Claude model and effort level for each agent, never the max effort |
| other-model-effort | `/other-model-effort` | the same choice for models that are not Claude, in light, all-round and top tiers |
| resource-guard | `/resource-guard` | checks memory, processor and disk before a heavy command, and waits if there is too little |
| progress-board | none, started by `/drive` | a local page at http://127.0.0.1:8790 that charts each run's percentage, started at every login |
| stop-resume-agents | `/stop-all`, `/resume-all` | stops everything, subagents included, and resumes later where each one was |
| using-git-worktrees | `/isolate` | isolates a piece of work in a separate working copy |
| writing-skills | `/write-skill` | writes or fixes a skill, and tests it on subagents |
| terse-speech | none, loaded at every session and subagent start | keeps every reply and every report between agents short and plain |
| least-code | none, loaded at every session and subagent start | makes the agent write the smallest change that fully works, and stop searching once it has the answer |
| code-map | none | maps a project's code and keeps notes on it from one session to the next: where things are defined and used, what calls what, dead code, import cycles, why the code is the way it is |
| secure-code-loop | `/secure-code-loop` | runs the security scanners found on the PC, fixes what they report and scans again until nothing serious is left |
| fabric-modding | none | writes and fixes Minecraft Java mods on Fabric: exact versions first, the docs of that version read before any code, names checked in the game sources, a build to prove it |
| neoforge-modding | none | the same for NeoForge mods |
| forge-modding | none | the same for Forge mods, including the event bus rewrite of Forge 1.21.6 |
| blender-3d | none | works in Blender: picks the tool among every option the manual lists, reads the docs page of the installed version before each action, proves the result with counts and a preview |

## License

MIT, see `LICENSE`. Copyright (c) 2026 Florent Leterme.
