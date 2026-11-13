---
name: resource-guard
description: Use when the user types /resource-guard, when a heavy command (build, tests, docker, dev server, package install) is about to run on a PC shared by several agent sessions, when the machine is slow, short of RAM or its disk is saturated, when a resource-guard hook blocked a shell call, or when a pre-tool resource check must be wired into Claude Code, Codex CLI, Gemini CLI or Qwen Code.
---

# Resource guard

Several agent sessions share one PC. Before heavy command, check there is room; wait when not.
`scripts/guard.py` measures with standard library only (no PowerShell, no psutil): call as
`python -I "<skill>/scripts/guard.py" <action>`, `<skill>` = this folder, absolute path, forward slashes.

## Actions

`guard.py` takes one of three actions.

| Action | What it does | Exit |
|---|---|---|
| `check` | one line: free RAM, CPU load, disk busy time, free space on current drive, then `ok` or `wait (<reasons>)` | 0 ok, 1 not |
| `wait` | re-checks every 5 s; one line when it starts waiting, one when done | 0 ok, 2 timeout |
| `hook` | reads pre-tool event on stdin, waits only when shell command is heavy | 0 go, 2 blocked |

Before heavy command, run `wait`, start only on exit 0 (in Claude Code installed hook already does this);
`check` only prints numbers. Heavy = build, test runner, docker, dev server, install, or script run through npm,
pnpm, yarn or bun, pip, uv or uvx, python, java, gradle, maven, cargo, rustc, go, dotnet, deno, tauri, tsc,
webpack, vitest, jest or playwright. Full list: pattern in `scripts/lib/heavy.py`.

## Thresholds

Flag beats environment variable, which beats default.

| Limit | Flag | Variable | Default |
|---|---|---|---|
| free RAM at least | `--ram-gb` | `RESOURCE_GUARD_RAM_GB` | 1.5 GB |
| CPU load at most | `--cpu` | `RESOURCE_GUARD_CPU` | 85 % |
| disk busy time at most | `--disk` | `RESOURCE_GUARD_DISK` | 100 % |
| longest wait | `--timeout` | `RESOURCE_GUARD_TIMEOUT` | 300 s |
| free disk space warning | none | `RESOURCE_GUARD_FREE_GB` | 20 GB |

Metric platform cannot give prints as `unknown`, never makes anyone wait (disk busy time on macOS, for one). Low
free space only prints warning line: waiting does not free disk, deleting own leftovers does.

## How the hook behaves

Hook runs before every shell call, so light command costs one Python start, nothing else: no sampling, no
output, exit 0. Reads command from `tool_input.command` (string, or list where leading `bash -lc` style wrapper
is dropped), `tool_input.cmd` or top-level `command`. Heredoc bodies and quoted text after `-m`, `--message`,
`--grep`, `-e`, `--regexp`, `rg` or `grep` are not read as commands, so commit messages and search patterns
never wait. Command calling `resource-guard/scripts/guard.py` is never held (word `resource-guard` elsewhere
does not count), so chain heavy command after `guard.py wait` with `&&`, never `;`. Light skill scripts run
through Python are not held either: browser-bidi's `bidi.py`, clean-code's `findings.py`, `score.py`,
`plan_check.py` and `measure.py`, strip-ai-traces' `scan.py`, clean-commits' `state.py`, progress-board's
`server.py`, stop-resume-agents' `agent_digest.py`, `resume_file.py` and `resume_check.py`, and
limited-run's `run.py list` and `run.py stop`. `run.py start` always held; heavy command chained after light
script still waits.

Heavy command waits as `wait` does; on timeout hook writes reason to stderr, exits 2, which blocks call and tells
agent why. After block, no retry loop: first finish or stop heavy job you started yourself (`run.py stop <name>`,
never `--all`: limited-run's records hold every session's tasks), or tell user PC is full. Unreadable input lets
call through.

## Wiring it into an agent

claude-skills installer adds Claude Code hook. To wire check into Codex CLI, Qwen Code, Gemini CLI or any other
agent, read `reference/wiring.md`.
