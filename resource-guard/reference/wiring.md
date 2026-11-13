# Wiring resource-guard into an agent

`<python>` = full path of Python 3 interpreter, `<repo>` = claude-skills clone, both written in full with
forward slashes. Hook timeout stays above `RESOURCE_GUARD_TIMEOUT` (330 s against 300 s) so guard answers
before agent kills it.

Claude Code: `PreToolUse` hook on matcher `Bash`, command `"<python>" -I "<repo>/resource-guard/scripts/guard.py" hook`,
timeout 330. claude-skills installer adds it; nothing to do by hand after install.

Codex CLI runs `PreToolUse` command hooks with one JSON object on stdin (`tool_name` is `Bash`, command in
`tool_input.command`), treats exit 2 as block with stderr text as reason, counts `timeout` in seconds. In
`~/.codex/config.toml`:

```toml
[[hooks.PreToolUse]]
matcher = "^Bash$"

[[hooks.PreToolUse.hooks]]
type = "command"
command = '"<python>" -I "<repo>/resource-guard/scripts/guard.py" hook'
timeout = 330
```

Codex asks for review of new hooks with `/hooks` before running them.

Qwen Code runs `PreToolUse` command hooks with JSON on stdin, takes `run_shell_command` as shell tool's matcher,
passes stderr to model on exit 2, counts `timeout` in seconds. In its `settings.json`:

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

Gemini CLI has `BeforeTool` hook fed JSON on stdin; exit 2 aborts tool with stderr as reason; counts `timeout`
in milliseconds. Same block as Qwen Code goes in its `settings.json` with `BeforeTool` in place of `PreToolUse`
and `"timeout": 330000`. Its hooks page does not name field carrying shell command; if none of the three the hook
reads (`tool_input.command`, `tool_input.cmd` or top-level `command`), hook sees no command, lets every call
through. So add instructions line below to `GEMINI.md` too.

Any other agent, or one whose hook does not fire: one line in its instructions file (`AGENTS.md`, `GEMINI.md`,
`QWEN.md`):

```text
Before any heavy command (build, tests, docker, dev server, install), run python -I "<repo>/resource-guard/scripts/guard.py" wait and start the command only if it exits 0.
```
