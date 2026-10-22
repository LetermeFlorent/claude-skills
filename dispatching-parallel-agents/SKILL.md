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

A subagent starts with an empty head and returns one conclusion. That makes it the right tool for
work that is wide but shallow: many files to read, a repetitive edit, a log to comb, a search across
a large tree. It is also the way to run independent problems at the same time. The main session
keeps the coordination and keeps only each agent's conclusion, never its working.

Parallel means independent, and independence is checked before the dispatch, not hoped for. Two
agents that write the same file, share a port or drive the same program do not save time, they
destroy each other's work.

## Rules that never bend

These hold for every dispatch, however urgent the request sounds.

1. Independence test first (below). One failed line and the two tasks run one after the other, or
   merge into one agent.
2. Several independent tasks go out in one message with several Agent calls. One call per message
   runs them one after the other.
3. Model: `sonnet` by default. `opus` only when the task is hard reasoning, a subtle bug or a design
   choice, and the reason is written in the dispatch. Never set the effort unless the user asks for it.
4. Each agent gets exact paths, a narrow scope, constraints and the shape of what it must return. It
   never inherits the session: everything it needs is in its prompt. `agent-brief.md` is the frame.
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

The pattern pays when the tasks are separate and each one is understood without the others. This
table sorts the common cases.

| Situation | Decision |
|---|---|
| Three test files fail, causes look unrelated | One agent per file, in parallel |
| Fixing one failure may fix the others | One agent for all, or the first alone, then re-run |
| 40 files to read for one question | Split by folder, read-only agents, conclusions merged |
| The same edit on 30 files | Split in groups, each group owns its files |
| You do not yet know what is broken | Investigate yourself first, dispatch after |
| Two tasks need the same file | Sequential, or one agent for both |
| One task needs the other's output | Sequential, in that order |

Exploratory debugging is not parallel work. Dispatch once the failures have names.

## Independence test

Write the plan as a list before dispatching: for each agent, the files it may write, its working
tree, the ports it will open, the MCP instances it drives, and whether it will run something heavy.
Then check every pair against these lines.

| Shared thing | Why it breaks | What to do |
|---|---|---|
| A file or a folder written by two agents | The second write erases the first | Split by file, or run one after the other |
| One working tree where both write | Edits and half-built states leak between them | Separate files in one tree is fine; two commits or two checkouts are not. Use an isolated copy when they must differ |
| The git index | Staged files of one end up in the other's commit | Agents never commit; the main session does |
| A dev server port | The second server fails or answers for the first | One port per agent, written in its prompt |
| A Chrome debugging port or profile | Two drivers on one browser | One port and one profile per agent, see chrome-bidi |
| A game editor, 3D editor or audio editor instance | Two agents edit one scene or one track | One instance per agent, `instance` passed explicitly in every call; an agent closes only its own |
| A docker image or container | Concurrent builds give an incoherent image | Main session builds once, before |
| A lockfile, a build output folder, a shared cache | Concurrent writes corrupt it | Read-only agents, or one agent |

To check a plan with a script, write it as JSON and run it. Each agent has `name`, `writes` (paths),
`tree`, `ports`, `instances`, and the flags `commits`, `heavy`, `rebuild`.

```text
python -I "<skill>/scripts/overlap.py" "<temp>/claude-skills/plan.json"
```

`<temp>` is the system temp folder (`tempfile.gettempdir()`).

Exit 0 says the agents are independent. Exit 2 lists the conflicts, one per line: fix the plan and
run it again. The script knows paths, ports and instance names; it cannot see a hidden shared
state, so the table above still applies.

## Procedure

Seven steps, in this order. The grill rule applies first: say in one sentence how big the request
reads, and ask only what the code and the situation do not answer.

1. Name the problems. Group the work by what is broken or what is asked, one name per domain: a
   test file, a subsystem, a folder to read. Fewer than two independent domains: do it yourself, or
   hand it to a single agent if it is only wide.
2. Write the plan and run the independence test. Merge or order the tasks that fail it.
3. Look at the machine once if any agent will run heavy commands: free RAM, CPU load, free disk, in
   one PowerShell call.
   ```text
   Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory
   (Get-CimInstance Win32_Processor).LoadPercentage
   Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" | Select FreeSpace,Size
   ```
   Under 1.5 GB free or CPU over 85 percent: do not stack. Dispatch fewer agents, or wait. Over the
   limit of two heavy processes: the others wait for a slot.
4. Do the one-time work yourself: the docker or next build, the install, the shared setup. Agents
   start from a ready tree.
5. Write one prompt per agent from `agent-brief.md`, then send them all in one message. Heavy
   commands inside an agent run at BelowNormal priority, with two workers at most (`--maxWorkers=2`,
   `-j2`) and a targeted run before a full one. Tell the agent so in its prompt.
6. Collect. Read each conclusion and nothing else. Check that no two touched the same file
   (`git status`, `git diff --stat`). An agent that stalls or goes off scope is stopped and removed
   at once. Long waits follow the waiting rule: wait for a line in a log with
   `for i in $(seq 120); do grep -qE '<done line>|<failure line>' <log> && break; sleep 2; done`, never for a
   duration alone.
7. Merge and verify. Run the full check yourself, in this message, and read the output. When the
   task asks for commits, hand the files to clean-commits, one intent per commit; otherwise say the
   tree is left uncommitted. Close servers and instances started during the dispatch, list the
   agents, remove the dead ones.

## Choosing the model

Most parallel tasks are narrow and well defined, which is sonnet work.

| Task | Model |
|---|---|
| Read these files and answer a question, list occurrences, comb a log | sonnet |
| Apply the same edit to a group of files | sonnet |
| Fix a failing test whose cause is local | sonnet |
| A race condition, a design trade-off, a bug that survived one attempt | opus, with the reason |

The effort is left to the default. It is raised only when the user asks for it.

## Stopping everything

When the user wants all work frozen, including the agents, and a record of what each was doing, the
`stop-resume-agents` skill does it: `/stop-all` stops and writes `resume.md`, `/resume-all`
relaunches the unfinished agents later. A dispatch can be abandoned at any point that way.

## Red flags

These thoughts mean the dispatch is about to go wrong.

| Thought | Reality |
|---|---|
| "It is urgent, launch eight opus agents on everything, high effort" | Urgent calls for the right split, not the heaviest. Independent domains only, sonnet by default, effort untouched. |
| "No time to look at the machine" | One call, a few seconds. Eight heavy agents on a loaded PC slow everything, yours included. |
| "They both edit config.json but different lines" | Same file means sequential. |
| "Each agent can commit its own work" | One index. The main session commits. |
| "Agent 3 can rebuild the image, it needs it" | It reports the need. The main session rebuilds once and re-dispatches. |
| "The agents said green, so it is green" | Run the full check yourself. |
| "I will read every agent's whole transcript" | The conclusion is enough. Detail only when two conclusions disagree. |
| "The agent is stuck, leave it, it may finish" | Stop it and remove it. A dead agent that stays is a leak. |
| "Three agents, one dev server on 3000 for all" | One port each, or no server. |
| "Two Blender agents can share the open scene" | One instance per agent, `instance` in every call. |

## Files

`agent-brief.md` is the frame of one agent prompt. `scripts/overlap.py` checks a dispatch plan for
shared files, ports, instances, commits, rebuilds and too many heavy agents; `scripts/lib/` holds
the plan reader and the rules. `tests/test_pure.py` is its unit test. `commands/paralleliser.md` is
the `/paralleliser` command, `LISEZMOI.md` the French notes.
