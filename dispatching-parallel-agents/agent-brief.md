# Agent prompt frame

Fill every field. An agent has none of the session's context, so a field left vague is a guess.

```text
Task: <one sentence, one domain>

Scope: you may read <paths>. You may write only <exact paths>. Nothing else is yours.

Context: <error messages pasted, test names, the cause you suspect and why, what was already tried>

Goal: <the observable result, for example "these 3 tests pass">

Constraints:
- Do not touch any other file, and do not change production code if the task is tests only.
- Do not run git commands that change state: no add, commit, stash, checkout, reset, push.
- Do not run docker build, docker compose build, next build or recreate a container. If you
  think one is needed, stop and say so in your report.
- Heavy commands: BelowNormal priority, 2 workers at most, targeted run before a full one.
- Port: <the one port this agent may open, or none>. MCP instance: <the instance this agent
  owns, or none>. Close only what you opened.
- Fix the root cause. Raising a timeout or skipping a test is not a fix.

Return, in this order, and nothing more:
1. Root cause or answer, in two sentences.
2. Files changed, one path per line.
3. The command you ran to check and its last output lines.
4. Anything you could not decide, as a question with its options and the one you took.
```

Agents cannot ask the user anything. A question goes in item 4 of the report, with its options; the
agent takes the recommended one and goes on.

For a read-only agent, the Scope line says "you write nothing", the Goal is the question to
answer, and the report is the answer with the paths and line numbers that support it.
