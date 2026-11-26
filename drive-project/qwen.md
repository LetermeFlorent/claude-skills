# Running /drive in Qwen Code

Read by lead and workers when the session runs in Qwen Code (its tools are named `agent`,
`run_shell_command`, `ask_user_question`). Where it differs from `SKILL.md` or `worker-brief.md`, this file
wins.

## Tool names

| In SKILL.md and worker-brief.md | In Qwen Code |
|---|---|
| Agent call named `c2` | `agent` with `description` = chain id (`c2`), `prompt`, `model` (a grade), `run_in_background` |
| SendMessage to `c2` | `list_agents`, `task_id` of the agent whose description is `c2`, then `send_message` |
| AskUserQuestion | `ask_user_question` |
| Bash | `run_shell_command` |
| Read, Write, Edit | `read_file`, `write_file`, `edit` |
| Monitor until-loop | background `run_shell_command` whose own loop waits for the line, read when it ends |
| ToolSearch | not needed |

## Mode, picked once

Lead picks mode at step 2 and writes `Mode: subagents` or `Mode: solo` in plan's top lines; resumed plan
keeps it.

- `subagents`: `agent` is in the tool list and the mapping worker's call returns a report.
- `solo`: no `agent` tool, the call is refused, or it ends with no report twice. Whole run stays solo.

## Subagents mode

Lead hands out chains as in SKILL.md, with these changes.

1. Model per chain = grade passed as `model`: row's Haiku = `light`, Sonnet = `all-round`, Opus = `top`
   (claude-model-effort tables); ceiling = grade of row's ceiling. A grade the tool rejects (not in `agents.modelGrades` or `agents.allowedGrades`):
   call again without `model`, plan row says `inherit`.
2. Effort cannot be set per call: every worker runs at session effort (`model.reasoningEffort`). Rows keep
   their effort word as a record only. Climbing (lead rule 4) moves grade only: `light` -> `all-round` ->
   `top`, never past ceiling's tier.
3. One `agent` call per message, each `run_in_background: true`: several calls in one message may return
   nothing on some versions. Chains still run side by side: start next chain in next message at once.
4. Report missing: `list_agents` shows its state. `resume_blocked_reason` on resend: fresh worker, same
   grade, `Earlier attempt:` = what `list_agents` gives.
5. Workers never start agents, so nesting depth 1 is enough. clean-code readers and verifier are agents
   of the `clean` worker: when it cannot start them, SKILL.md step 6 last paragraph applies.

## Solo mode

No worker exists: lead does every chain itself. Lead rule "never does project work" is lifted; every
other rule holds.

1. Mapping and run kit, from step 2 on: lead follows `start-brief.md`; run kit's commands run in background
   shells while questions are asked.
2. Chains one at a time, in plan order, `after:` respected. Before each chain, reread `worker-brief.md`
   Rules; read only that chain's files and lessons.
3. After each chain: its WORKER REPORT written under the chain in plan, boxes ticked, percentage posted.
   Nothing from that chain is kept in mind beyond its report: next chain rereads what it needs.
4. Box check fails: one more attempt with failing lines reread from scratch; fails again: run ends like a
   blocked box (no stronger model to climb to).
5. Review chain at *beaucoup* and *max*: lead reviews diff per worker-brief's review rule, after rereading
   files whole, never from memory of writing them.
6. `clean`: clean-code alone, Audit steps 1 to 5, then its verifier's brief
   (`<repo>/clean-code/verify-brief.md`) followed by lead itself, then Audit step 7 on.

## Worker part

Workers, and lead in solo mode, follow these on top of worker-brief.md.

- Wait for a line: one background `run_shell_command` running
  `until grep -q "<line>" <file>; do sleep 2; done`, read when it ends. Never a bare `sleep`.
- resource-guard hook runs when the user wired it (`resource-guard/reference/wiring.md`); unsure: run
  `python -I <repo>/resource-guard/scripts/guard.py wait` once before the chain's first heavy command.
- Final block unchanged; in solo mode lead writes it into plan, nowhere else.

## Settings for speed

User's `~/.qwen/settings.json`, set once by the user, never by the run:

```json
{
  "model": { "reasoningEffort": "medium" },
  "agents": {
    "modelGrades": { "light": "fast", "all-round": "<all-round model id>", "top": "<strongest model id>" },
    "allowedGrades": ["light", "all-round", "top"]
  }
}
```

Qwen3.8-Flash-Next thinks at `xhigh` by default: `medium` keeps workers fast; a chain failing twice climbs
grade, not effort. Run on Flash-Next alone: all three grades point at it, climbing then changes nothing and
a box failing at `top` ends run.
