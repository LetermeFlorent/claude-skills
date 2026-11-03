---
name: limited-run
description: Use when about to start a dev server, watcher, build, test run, docker container or any long command on a machine shared with other agent sessions, when RAM runs low or the PC slows down, when an earlier turn left node, vite, vitest, jest, java, gradle or python processes running, or before ending a turn or a session that started processes.
---

# Running task processes with a cap, then closing them

Several agent sessions share one machine. Each process an agent starts takes RAM and CPU from all the others
until someone stops it, and a dev server or watcher left behind keeps doing so for hours. So every task process
starts with a RAM cap and low priority, is tracked, and is stopped as soon as its result is in hand.

`<skill>` is this folder. The script needs Python 3, standard library only:

```
python -I "<skill>/scripts/run.py" start [--ram-mb N] [--name NAME] [--cwd DIR] -- <command...>
python -I "<skill>/scripts/run.py" list
python -I "<skill>/scripts/run.py" stop NAME|PID
python -I "<skill>/scripts/run.py" stop --all
```

`start` runs the command, waits for it and returns its exit code (2 is a refusal, 1 a failure of the tool,
128 plus the signal number when the launcher was stopped). It prints one line first:
`limited-run: <name> pid <pid>, cap <N> MB, below normal priority`. The default cap is half of the free RAM,
between 512 and 4096 MB; `--ram-mb 0` drops the memory cap and keeps the low priority. The default name is the
command's first word plus a counter (`npm-1`); a name already used by a live task is refused.

| System | What `start` does |
|---|---|
| Windows | A Job Object holds the whole tree: one RAM cap for all its processes together, below normal priority, and the tree dies with the launcher, even when the launcher is killed. The command starts suspended and joins the job before it runs, so no child escapes. |
| Linux, macOS | New session, `nice` 10, and `RLIMIT_AS` at the cap. That limit applies to each process on its own, not to the tree, and it counts address space: node and JVMs reserve far more than they use, so give them `--ram-mb 0` and the runtime's own cap below. |

Ctrl+C or SIGTERM on the launcher stops the whole tree and removes the record. Records live in
`<system temp>/limited-run/` (or the folder in `LIMITED_RUN_STATE`); `list` drops those whose launcher died.

## Rules

These hold for every agent, in every project.

1. Every dev server, watcher, build, test run and container goes through `run.py start`. When the agent cannot
   wrap a command (a tool runs it for you), give the runtime its own cap, picked from free RAM the same way:

   | Runtime | Cap |
   |---|---|
   | node, vite, next | `node --max-old-space-size=<MB>`, or `NODE_OPTIONS=--max-old-space-size=<MB>` |
   | java | `-Xmx<MB>m`; gradle: `org.gradle.jvmargs=-Xmx<MB>m` in `gradle.properties` |
   | vitest, jest | `--maxWorkers=2` |
   | make, cargo | `-j2` |
   | turbo, lerna | `--concurrency 2`; pnpm: `--workspace-concurrency 2`; nx: `--parallel=2` |
   | docker | `docker run --memory <MB>m --cpus 1`; compose: `mem_limit` and `cpus` under the service |

   Inside `run.py start` the runtime cap still helps: set the node heap or `-Xmx` to about three quarters of
   the cap, since the cap counts the whole process and the heap is only part of it.
2. A long-lived process (server, watcher) runs in the agent's background mode, still wrapped:
   `run_in_background` in Claude Code, or the agent's equivalent. Never `&` alone, `nohup` or `start /b`
   without the wrapper.
3. Stop each task the moment its result is in hand: the page loaded, the test passed or failed, the build
   finished. `stop <name>` stops the whole tree.
4. Before ending a turn or a session, run `list` and `stop` what is left. A task kept on purpose for the user
   (a preview they are looking at) is named in the reply with the command that stops it.
5. Never stop a process this tool did not start, even one that looks like a leftover: another session may own
   it. `stop` only acts on records this tool wrote, and checks the process is still the one recorded.

## Following this from other agents

Claude Code reads this folder as a skill. Codex CLI, Gemini CLI and Qwen Code do not load skills: add one line
to their instructions file (`AGENTS.md` for Codex CLI, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code),
global or per project, for example:

```
Start every server, watcher, build and test run as described in <absolute path>/limited-run/SKILL.md, and stop them before ending.
```

Any other agent that reads an instructions file takes the same line. Hooks that enforce this are not part of
the skill.
