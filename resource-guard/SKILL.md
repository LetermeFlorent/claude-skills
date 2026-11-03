---
name: resource-guard
description: Use when the user types /resource-guard, when a heavy command (build, tests, docker, dev server, package install) is about to run on a PC shared by several agent sessions, when the machine is slow, short of RAM or its disk is saturated, when a resource-guard hook blocked a shell call, or when a pre-tool resource check must be wired into Claude Code, Codex CLI, Gemini CLI or Qwen Code.
---

# Resource guard

Several agent sessions share one PC. Before a heavy command, check that there is room for it, and wait when
there is not. `scripts/guard.py` does the measuring with the standard library only (no PowerShell, no
psutil): call it as `python -I "<skill>/scripts/guard.py" <action>`, absolute path, forward slashes.

## Actions

| Action | What it does | Exit |
|---|---|---|
| `check` | one line: free RAM, CPU load, disk busy time, free space on the current drive, then `ok` or `wait (<reasons>)` | 0 ok, 1 not |
| `wait` | re-checks every 5 s; one line when it starts waiting, one when done | 0 ok, 2 timeout |
| `hook` | reads a pre-tool event on stdin and waits only when the shell command is heavy | 0 go, 2 blocked |

Run `check` before starting something heavy by hand, and `wait` when a script or another agent needs to
block until the PC has room. A heavy command is a build, a test runner, docker, a dev server, an install or
a script run through npm, pnpm, yarn or bun, python, java, gradle, maven, cargo, go, dotnet, tauri, tsc,
webpack, vitest, jest or playwright. The full list is the pattern in `scripts/lib/heavy.py`.

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
leading `bash -lc` style wrapper is dropped), `tool_input.cmd` or a top-level `command`. Commands that call
resource-guard itself are never held. A heavy command waits as `wait` does; on timeout the hook writes the
reason to stderr and exits 2, which blocks the call and tells the agent why. After a block, do not retry in
a loop: finish or stop another heavy job first, or tell the user the PC is full. Unreadable input lets the
call through.

## Wiring it into an agent

`<python>` is the full path of a Python 3 interpreter and `<repo>` the claude-skills clone, both written out
in full with forward slashes. The hook timeout stays above `RESOURCE_GUARD_TIMEOUT` (330 s against 300 s) so
the guard can answer before the agent kills it.

Claude Code: a `PreToolUse` hook on matcher `Bash`, command `"<python>" -I "<repo>/resource-guard/scripts/guard.py" hook`,
timeout 330. The claude-skills installer adds it, so there is nothing to do by hand after an install.

Codex CLI runs `PreToolUse` command hooks with one JSON object on stdin (`tool_name` is `Bash`, the command
is in `tool_input.command`), treats exit 2 as a block with the stderr text as reason, and counts `timeout` in
seconds. In `~/.codex/config.toml`:

```toml
[[hooks.PreToolUse]]
matcher = "^Bash$"

[[hooks.PreToolUse.hooks]]
type = "command"
command = '"<python>" -I "<repo>/resource-guard/scripts/guard.py" hook'
timeout = 330
```

Codex asks for a review of new hooks with `/hooks` before it runs them.

Qwen Code runs `PreToolUse` command hooks with JSON on stdin, takes `run_shell_command` as the shell tool's
matcher, passes stderr to the model on exit 2, and counts `timeout` in seconds. In its `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "run_shell_command",
        "hooks": [
          {
            "type": "command",
            "command": "\"<python>\" -I \"<repo>/resource-guard/scripts/guard.py\" hook",
            "name": "resource-guard",
            "timeout": 330
          }
        ]
      }
    ]
  }
}
```

Gemini CLI has a `BeforeTool` hook fed JSON on stdin, whose exit 2 aborts the tool with stderr as the
reason, and counts `timeout` in milliseconds. The same block as Qwen Code goes in its `settings.json` with
`BeforeTool` in place of `PreToolUse` and `"timeout": 330000`. Its hooks page does not name the field that
carries the shell command; if it is none of the three above, the hook sees no command and lets every call
through. So add the instructions line below to `GEMINI.md` as well.

Any other agent, or one whose hook does not fire: one line in its instructions file (`AGENTS.md`,
`GEMINI.md`, `QWEN.md`):

```text
Before any heavy command (build, tests, docker, dev server, install), run python -I "<repo>/resource-guard/scripts/guard.py" wait and start the command only if it exits 0.
```
