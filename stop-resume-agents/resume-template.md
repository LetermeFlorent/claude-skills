# Shape of resume.md

resume.md is written in English. Keep the first line, the `State:` line and every `## Agent <id>`
heading exactly as below: /resume-all and `scripts/resume_check.py` look for them, and the checker
refuses any placeholder of this template left in the file. A field with nothing to say gets `none`.
Verbatim blocks use four backticks, because reports often hold three. While answers are awaited a
field reads `pending <agent id>`, never a bare `pending`, so Edit can target one section.

`````markdown
<!-- stop-resume-agents v1 -->
# Stop-all resume

State: STOP IN PROGRESS
Stop requested on <YYYY-MM-DD HH:MM> (local time), origin session <session id>.
Claude account: <value of CLAUDE_CONFIG_DIR, or ~/.claude if empty>.
Working folder: <absolute path>. Nothing was committed or pushed by the stop.

## Starting request

````text
<the user's request, word for word>
````

## Main session

What I was doing at the stop: <exact step, file and line, last command and its useful output>
Done and verified: <list>
Still to do, in order: <numbered list>
Decisions made and approaches rejected: <list>
Internal task list: <items done and not done>

## Repository state

One block per repository touched, raw output:

````text
<path>  branch <name>  HEAD <short sha> <commit subject>
<git status --short>
<git diff --stat>
<git stash list>
````

## Agent <id> : <description>

Type: <agentType>. Model: <model>. Effort: <effort>. Depth: <1 or 2, parent if 2>.
Started at <time>, last activity at <time>.
Answer at stop: <yes, at HH:MM | no, rebuilt from its log | no, finished before the stop>
Status: <done | partial | not started | unknown>
To relaunch: <yes | no, because ...>
Relaunch order: <1, 2, ... ; after agent <id> if it depends on it ; in parallel otherwise>
Files it owns: <one line per file, fingerprint from resume_file.py hash then absolute path>

### Starting brief

````text
<the original prompt, word for word, taken from the digest>
````

### Its report

````text
<the AGENT REPORT block, word for word, or "no answer">
````

### Main session findings

<what the digest and git show: files written, last commands, subagents started;
any gap between its report and the disk, written plainly>

## Processes, background tasks and tools stopped

One item per line: what, exact command, folder, PID or port or id, how it was stopped,
how to relaunch it, whether it must be relaunched. Includes background Bash commands, servers,
/loop loops, scheduled tasks, workflows, Chrome ports. Nothing was running: `none`.

## Open questions

<questions asked or to ask the user, or none>

## Resume plan

1. <agent id or main session>: <action> (<depends on ...>)
2. ...

## Log

- <YYYY-MM-DD HH:MM> stopped by /stop-all, session <id>, <n> agents, <n> without an answer
`````

When the digest prints `PROMPT NOT FOUND` and neither your context nor the parent's digest holds the
prompt, keep that text in the block and add `Brief lost: <why>` under it.

States: `STOP IN PROGRESS`, then `STOPPED` when complete. Each /resume-all adds a `## Resumed on <date>`
section above `## Log`, a Log line, and sets `State: RESUMED on <YYYY-MM-DD HH:MM>, session <id>`.
A file taken over by a newer /stop-all of the same session reads `State: REPLACED by <path of the new
file>`; /resume-all skips it.
