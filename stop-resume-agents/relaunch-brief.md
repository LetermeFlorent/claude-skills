# Prompts for resumed subagents

Two texts live here. The first is the Agent `prompt` of a new agent that takes over. The second
is the SendMessage that wakes the old agent itself, when resume.md was written by this same
session. Fill every `<...>` from the agent's section of resume.md and from the reality check.
Never leave a placeholder in the sent text.

## New agent

````text
You are taking over a task that another agent started and that was stopped on <date of stop>. Do not start over: finish it.

ORIGINAL MISSION, word for word as the first agent received it:
<original prompt>

WHAT THE FIRST AGENT REPORTED WHEN IT WAS STOPPED:
<AGENT REPORT block, or: "it did not answer; what follows comes from its transcript">

SUBAGENTS IT HAD STARTED, AND THEIR REPORTS:
<one entry per child agent with its report, or "none". Start a new subagent only for work that is still left.>

STATE CHECKED ON DISK TODAY, BEFORE YOUR LAUNCH:
<git branch and status of the files it owns, files that exist or not, anything that changed since the stop and who changed it if known>

KNOWN DIFFERENCES, ACCEPTED BY THE USER, NOT A CONTRADICTION:
<each accepted drift and what to do with it, for example "commit abc123 changed X: keep it and build on top", or "none">

WORKING DIRECTORY: your shell may start elsewhere. The project is <absolute project path>. Use absolute paths and `git -C <project path>` for every command. Read the CLAUDE.md files of that project before your first edit: their rules bind you.

WHAT YOU DO, IN THIS ORDER:
1. Re-read every file you are about to edit before editing it: line numbers in the report may have moved.
2. Check that the steps reported as done are really done. Do not redo a step that is done and correct.
3. Continue with these remaining steps: <numbered list>.
4. Verify your work the way the original mission asks, then stop.

LIMITS:
- Files you may modify: <owned files, absolute paths>. Other work happens at the same time on <files owned by other agents and by the main session, or "nothing else">. Do not touch those files.
- Do not commit or push unless the original mission says so. Never add resume.md or resume-*.md to git.
- If what you find on disk contradicts the report in a way not listed under KNOWN DIFFERENCES, stop and say so in your final answer instead of guessing.
- If you receive a message starting with STOP-ALL, obey it at once.

FINAL ANSWER: what you did, files changed with absolute paths, how you verified it, what is left.
````

## Old agent woken by SendMessage

Send it to the old agent id. It keeps its whole memory, so the text only lifts the stop and says
what changed. If no notification or new activity shows within two rounds of `sleep 30` (check
with `agent_digest.py --agent <id> --out "<scratch>/digest-<id>.md"`: its last activity must move), launch a new agent with the
text above instead, and write it in the Reprise section.

````text
RESUME-ALL: the STOP-ALL you received earlier is cancelled. Go back to your task and finish it.
State checked on disk today: <git branch and status of your files, anything that changed since the stop and who changed it>.
Known differences accepted by the user, not a contradiction: <list, or "none">.
Remaining steps, in this order: <numbered list from your report>.
Re-read every file before editing it. Same limits as your original mission; files owned by other agents right now: <list, or "none">. Do not commit or push unless your mission says so, never add resume.md to git.
If you receive a message starting with STOP-ALL, obey it at once.
Final answer: what you did, files changed with absolute paths, how you verified it, what is left.
````
