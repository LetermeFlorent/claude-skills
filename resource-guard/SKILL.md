---
name: resource-guard
description: Use when the user types /resource-guard, when a heavy command (build, tests, docker, dev server, package install) is about to run on a PC shared by several agent sessions, when the machine is slow, short of RAM or its disk is saturated, when a resource-guard hook blocked a shell call, or when a pre-tool resource check must be wired into Claude Code, Codex CLI, Gemini CLI or Qwen Code.
---

# Resource guard

Several agent sessions share one PC. Before a heavy command, check that there is room for it, and wait when
there is not. `scripts/guard.py` does the measuring with the standard library only (no PowerShell, no
psutil): call it as `python -I "<skill>/scripts/guard.py" <action>`, where `<skill>` is this folder, written
as an absolute path with forward slashes.

## Actions

`guard.py` takes one of three actions.

| Action | What it does | Exit |
|---|---|---|
| `check` | one line: free RAM, CPU load, disk busy time, free space on the current drive, then `ok` or `wait (<reasons>)` | 0 ok, 1 not |
| `wait` | re-checks every 5 s; one line when it starts waiting, one when done | 0 ok, 2 timeout |
| `hook` | reads a pre-tool event on stdin and waits only when the shell command is heavy | 0 go, 2 blocked |

Before a heavy command, run `wait` and start only on exit 0 (in Claude Code the installed hook already does
this); `check` only prints the numbers. A heavy command is a build, a test runner, docker, a dev server, an
install or a script run through npm, pnpm, yarn or bun, python, java, gradle, maven, cargo, go, dotnet, tauri,
tsc, webpack, vitest, jest or playwright. The full list is the pattern in `scripts/lib/heavy.py`.

## Thresholds

A flag beats the environment variable, which beats the default.

| Limit | Flag | Variable | Default |
|---|---|---|---|
| free RAM at least | `--ram-gb` | `RESOURCE_GUARD_RAM_GB` | 1.5 GB |
| CPU load at most | `--cpu` | `RESOURCE_GUARD_CPU` | 85 % |
| disk busy time at most | `--disk` | `RESOURCE_GUARD_DISK` | 100 % |
| longest wait | `--timeout` | `RESOURCE_GUARD_TIMEOUT` | 300 s |
| free disk space warning | none | `RESOURCE_GUARD_FREE_GB` | 20 GB |

A metric the platform cannot give is printed as `unknown` and never makes anyone wait (disk busy time on
macOS, for one). Low free space only prints a warning line: waiting does not free a disk, deleting your own
leftovers does.

## How the hook behaves

The hook runs before every shell call, so a light command costs one Python start and nothing else: no
sampling, no output, exit 0. It reads the command from `tool_input.command` (a string, or a list where a
leading `bash -lc` style wrapper is dropped), `tool_input.cmd` or a top-level `command`. Any command whose
text contains `resource-guard` is never held, so chain a heavy command after `guard.py wait` with `&&`, never
`;`. Light skill scripts run through Python are not held either: chrome-bidi's `bidi.py`, clean-code's
`findings.py`, `score.py`, `plan_check.py` and `measure.py`, strip-ai-traces' `scan.py`, clean-commits'
`state.py`, progress-board's `server.py`, and limited-run's `run.py list` and `run.py stop`. `run.py start` is
always held, and a heavy command chained after a light script still waits.

A heavy command waits as `wait` does; on timeout the hook writes the reason to stderr and exits 2, which
blocks the call and tells the agent why. After a block, do not retry in a loop: finish or stop a heavy job you
started yourself first (`run.py stop <name>`, never `--all`: limited-run's records hold every session's
tasks), or tell the user the PC is full. Unreadable input lets the call through.

## Wiring it into an agent

The claude-skills installer adds the Claude Code hook. To wire the check into Codex CLI, Qwen Code, Gemini
CLI or any other agent, read `reference/wiring.md`.
