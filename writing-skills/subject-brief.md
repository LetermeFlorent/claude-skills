# Subject brief

The prompt of one test subject: a fresh subagent on `sonnet`, launched with the Agent tool, never a
fork. Fill every `<...>` and send the first block as it is. The baseline and the green run get the
same text and differ by the skill line only; a baseline with no skill at all drops that line.
Drop the stand-in item when the skill writes nowhere but the fixture.

`````text
This is a real task, not a quiz. Act; do not describe what you would do.

<the scenario prompt, as the user would type it>

Read the skill at <absolute path of the SKILL.md under test> and follow it for this task.

Test rules, which are not part of the task:
- The user cannot answer you. Write every question you would ask them under a QUESTIONS heading in
  your report, with its options and the one you recommend first, then take that option and go on.
- For this run, <run>/home stands for the user's home folder, <run>/Desktop for its Desktop folder and
  <run>/tmp for <temp>/claude-skills, <temp> being the system temp folder. Use the stand-in wherever the task or a
  skill names the real path. A script of an existing skill runs from its real path; only what you
  write goes to the stand-ins.
- You may read any file on this machine. You write only under <run>. No push, no network, no board.
- A subagent you launch gets these test rules in its prompt, word for word, and runs on sonnet.

End with this report and nothing after it:
SUBJECT REPORT
steps, in order: <what you did, one line each>
subagents: <each one: its prompt in one line, its model, what it did>
files written: <absolute paths>
commands that decided something, with their output: <command, then the deciding lines>
shortcuts considered, taken or refused, and why: <in your own words>
QUESTIONS: <each question, its options, the one taken; or none>
`````

## Follow-up

When a subject read the skill and still did the wrong thing, continue the same agent with
SendMessage, before it is removed:

`````text
You read the skill and <what it did>. The expected action was <the right one>.
Do not redo the task. Answer in three lines at most: was the skill clear and you chose otherwise,
should it have said something it does not (quote the words you needed), or did you miss a section
(which one)?
`````

"Clear, I chose otherwise" calls for a foundational line early in the skill. "It should have said"
gets its words added, close to verbatim. "I missed it" moves the rule up, into the rules or the red
flags.
