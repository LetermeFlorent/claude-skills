# Message sent to each subagent on /stop-all

Send this text unchanged with SendMessage, one call per subagent, all calls in the same turn.
It was tested live: a running agent reads it at its next tool round, stops, and answers with
the filled template as its final answer, which reaches the main session as a task notification.
An agent that had already finished is woken up by the message and answers the same way.

````text
STOP-ALL: the main session is stopping all work now, reply with a status report and end your turn.
Stop your task immediately: no new step, no new command, no new edit. If a single file write is half done, finish only that write so no file is left broken, nothing else. Do not commit, stash, reset, format or clean anything.
If you started subagents yourself, send them this same message first, wait for their reports, stop them, and paste each report under yours with its agent id.
Then give your final answer, with no further tool call, using exactly this template (write "none" when a field is empty, never drop a field, write "unknown" rather than guess):

AGENT REPORT
Mission: your task in one sentence, as you understood it
Status: done | partial | not started
Done and verified: every finished step, with how you know it worked
In progress at stop: exact step, file and line, last command run and its useful output
Files created: absolute paths
Files modified: absolute path, what changed, line numbers
Files read for context: absolute paths that matter to understand the work
State-changing commands: installs, migrations, git operations, servers started (command, PID, port)
Still running from you: commands, processes or subagents you started that may still run, or none
Remaining steps in order: numbered, precise enough to run without asking
Decisions and rejected approaches: what you chose and why, what failed
Blockers and open questions: anything that needs the user or another agent
Resume instructions: what the agent that takes over must check and do first
END REPORT
````
