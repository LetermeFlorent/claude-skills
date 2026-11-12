# Wiring resource-guard into an agent

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
carries the shell command; if it is none of the three the hook reads (`tool_input.command`, `tool_input.cmd`
or a top-level `command`), the hook sees no command and lets every call through. So add the instructions line below to `GEMINI.md` as well.

Any other agent, or one whose hook does not fire: one line in its instructions file (`AGENTS.md`,
`GEMINI.md`, `QWEN.md`):

```text
Before any heavy command (build, tests, docker, dev server, install), run python -I "<repo>/resource-guard/scripts/guard.py" wait and start the command only if it exits 0.
```
