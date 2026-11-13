---
name: limited-run
description: Use when the user types /limited-run, when about to start a dev server, watcher, build, test run, docker container or any long command on a machine shared with other agent sessions, when RAM runs low or the PC slows down, when an earlier turn left node, vite, vitest, jest, java, gradle or python processes running, or before ending a turn or a session that started processes.
---

# Running task processes with a cap, then closing them

Several agent sessions share one machine. Each started process takes RAM and CPU from all others until stopped;
dev server or watcher left behind does so for hours. So every task process starts with RAM cap and low
priority, is tracked, and stops as soon as its result is in hand.

`<skill>` = this folder. Script needs Python 3, standard library only:

```
python -I "<skill>/scripts/run.py" start [--ram-mb N] [--name NAME] [--queue S] [--cwd DIR] -- <command...>
python -I "<skill>/scripts/run.py" list
python -I "<skill>/scripts/run.py" stop NAME|PID
python -I "<skill>/scripts/run.py" stop --all
```

`start` runs command, waits, returns its exit code. Just before command runs, prints one line:
`limited-run: <name> pid <pid>, cap <N> MB, below normal priority`. After that line exit code is command's, or
128 plus signal number when launcher was stopped; without that line, 2 = refusal (`refused: ...`), 1 = tool
failure. Default cap: half of free RAM, between 512 and 4096 MB; `--ram-mb 0` drops memory cap, keeps low
priority. Default name: command's first word plus counter (`npm-1`). Name used by live task is refused, unless
`--queue S` comes with `--name`: `start` then prints `limited-run: waiting for <name>` once, takes name as soon
as that task ends, refuses only after S seconds. So one name works as lock between agents.

| System | What `start` does |
|---|---|
| Windows | Job Object holds whole tree: one RAM cap for all its processes together, below normal priority, tree dies with launcher, even when launcher is killed. Command starts suspended, joins job before it runs, so no child escapes. |
| Linux, macOS | New session, `nice` 10, `RLIMIT_AS` at cap. Limit applies per process, not per tree, and counts address space: node and JVMs reserve far more than they use, so give them `--ram-mb 0` and runtime's own cap below. |

Ctrl+C or SIGTERM on launcher stops whole tree, removes record. Records live in `<system temp>/limited-run/`
(or folder in `LIMITED_RUN_STATE`); `list` drops those whose launcher died.

## Rules

Hold for every agent, every project.

1. Every dev server, watcher, build, test run and container goes through `run.py start`. When agent cannot wrap
   command (a tool runs it for you), give runtime its own cap, picked from free RAM same way:

   | Runtime | Cap |
   |---|---|
   | node, vite, next | `node --max-old-space-size=<MB>`, or `NODE_OPTIONS=--max-old-space-size=<MB>` |
   | java | `-Xmx<MB>m`; gradle: `org.gradle.jvmargs=-Xmx<MB>m` in `gradle.properties` |
   | vitest, jest | `--maxWorkers=2` |
   | make, cargo | `-j2` |
   | turbo, lerna | `--concurrency 2`; pnpm: `--workspace-concurrency 2`; nx: `--parallel=2` |
   | docker | `docker run --memory <MB>m --cpus 1`; compose: `mem_limit` and `cpus` under service |

   Inside `run.py start` runtime cap still helps: set node heap or `-Xmx` to about three quarters of cap, since
   cap counts whole process and heap is only part of it.
2. Long-lived process (server, watcher) runs in agent's background mode, still wrapped: `run_in_background` in
   Claude Code, or agent's equivalent. Never `&` alone, `nohup` or `start /b` without wrapper. Build or test run
   that may outlast shell timeout also runs in background mode, or with longer timeout.
3. Stop each task the moment its result is in hand: page loaded, test passed or failed, build finished.
   `stop <name>` stops whole tree.
4. Before ending turn or session, stop each name you started, read from its `limited-run: <name>` line. Records
   are shared by every session on machine, so never `stop --all`, never stop a name you did not start. Task kept
   on purpose for user (a preview they look at) is named in reply with command that stops it.
5. Never stop process this tool did not start, even one that looks like leftover: another session may own it.
   `stop` only acts on records this tool wrote, and checks process is still the one recorded.

## Following this from other agents

Claude Code reads this folder as skill. Codex CLI, Gemini CLI and Qwen Code do not load skills: add one line to
their instructions file (`AGENTS.md` for Codex CLI, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code), global
or per project, for example:

```
Start every server, watcher, build and test run as described in <absolute path>/limited-run/SKILL.md, and stop them before ending.
```

Any other agent reading instructions file takes same line. Hooks enforcing this are not part of skill.
