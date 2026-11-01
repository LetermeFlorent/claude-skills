---
name: dispatching-parallel-agents
description: Use when the user types /paralleliser, when two or more tasks can run without waiting on each other (several failing test files with different causes, separate subsystems, many files to read or edit the same way, large searches, log analysis), when wide but shallow work would flood the main context, or before sending several subagents at once and checking they cannot step on each other.
---

# Dispatching parallel agents

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

A subagent starts with an empty head and returns one conclusion, so it suits work that is wide but
shallow (many files to read, a repetitive edit, a log to comb) and independent problems run at the
same time. The main session keeps the coordination and only each agent's conclusion.

Parallel means independent, and independence is checked before the dispatch, not hoped for. Two
agents that write the same file, share a port or drive the same program destroy each other's work.

## Rules that never bend

These hold for every dispatch, however urgent the request sounds.

1. Independence test first (below). One failed line and the two tasks run one after the other, or
   merge into one agent.
2. Several independent tasks go out in one message with several Agent calls. One call per message
   runs them one after the other.
3. Model: `sonnet` by default. `opus` only for hard reasoning (a race, a design trade-off, a bug that
   survived one attempt), with the reason written in the dispatch. Never set the effort unless the
   user asks for it.
4. Each agent gets exact paths, a narrow scope, constraints and the shape of what it must return,
   because it never inherits the session. `agent-brief.md` is the frame.
5. No agent builds docker or next images, runs `docker compose build` or recreates a container. The
   main session does it once, before the dispatch, and says so in the prompts. An agent that thinks
   it needs a rebuild reports it and stops.
6. No agent commits, pushes or touches git state. Commits come from the main session, through
   clean-commits, once the merged result is checked.
7. Resources are looked at once, before the dispatch, when an agent will run heavy commands. At most
   two heavy processes at a time in the session, whatever the number of agents.
8. The main session runs the final check itself. An agent's "all green" is a lead, not a result.
9. A stopped agent is removed at once. The agent list is checked before closing and no dead agent
   stays.

## When to dispatch

Exploratory debugging is not parallel work: dispatch once the failures have names. These cases are
the ones that need a decision.

| Situation | Decision |
|---|---|
| Three test files fail, causes look unrelated | One agent per file, in parallel |
| Fixing one failure may fix the others | One agent for all, or the first alone, then re-run |
| 40 files to read for one question | Split by folder, read-only agents, conclusions merged |
| Two tasks need the same file, or one needs the other's output | Sequential, or one agent for both |

## Independence test

Write the plan as a list before dispatching: for each agent, the files it may write, its working
tree, the ports it will open, the MCP instances it drives, and whether it will run something heavy.
Then check every pair against these lines.

| Shared thing | What to do |
|---|---|
| A file or a folder written by two agents | Split by file, or run one after the other. Same file on different lines is still the same file |
| One working tree | Separate files in one tree is fine; two commits or two checkouts are not. Use an isolated copy when they must differ |
| A dev server port | One port per agent, written in its prompt |
| A Chrome debugging port or profile | One port and one profile per agent, see chrome-bidi |
| A game editor, 3D editor or audio editor instance | One instance per agent, `instance` passed explicitly in every call; an agent closes only its own |
| A lockfile, a build output folder, a shared cache | Read-only agents, or one agent |

To check a plan with a script, write it as JSON and run it. Each agent has `name`, `writes` (paths),
`tree`, `ports`, `instances`, and the flags `commits`, `heavy`, `rebuild`.

```text
python -I "<skill>/scripts/overlap.py" "<temp>/claude-skills/plan.json"
```

`<temp>` is the system temp folder (`tempfile.gettempdir()`). Exit 0 says the agents are independent.
Exit 2 lists the conflicts, one per line: fix the plan and run it again. The script knows paths,
ports and instance names; it cannot see a hidden shared state, so the table above still applies.

## Procedure

The grill rule applies first: say in one sentence how big the request reads, and ask only what the
code and the situation do not answer.

1. Name the problems, one per domain: a test file, a subsystem, a folder to read. Fewer than two
   independent domains: do it yourself, or hand it to a single agent if it is only wide.
2. Write the plan and run the independence test. Merge or order the tasks that fail it.
3. When an agent will run heavy commands, look at the machine once, in one PowerShell call.
   ```text
   Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory
   (Get-CimInstance Win32_Processor).LoadPercentage
   Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" | Select FreeSpace,Size
   ```
   Under 1.5 GB free or CPU over 85 percent: dispatch fewer agents, or wait.
4. Do the one-time work yourself (the docker or next build, the install, the shared setup). Agents
   start from a ready tree.
5. Write one prompt per agent from `agent-brief.md`, then send them all in one message.
6. Collect. Read each conclusion and nothing else, unless two disagree. Check that no two touched the
   same file (`git status`, `git diff --stat`). An agent that stalls or goes off scope is stopped and
   removed at once. A long command is run with `run_in_background` and awaited by its notification,
   never by a sleep loop.
7. Merge and verify. Run the full check yourself, in this message, and read the output. When the
   task asks for commits, hand the files to clean-commits, one intent per commit; otherwise say the
   tree is left uncommitted. Close servers and instances started during the dispatch, list the
   agents, remove the dead ones.

## Stopping everything

When the user wants all work frozen, including the agents, with a record of what each was doing, the
`stop-resume-agents` skill does it: `/stop-all` stops and writes `resume.md`, `/resume-all`
relaunches the unfinished agents later.
