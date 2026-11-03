# stop-resume-agents

A skill and two commands to stop all the work in progress, subagents included, then pick it up again later. To install it, see `INSTALL.md` at the root of the repository.

## /stop-all

Claude stops its own work and asks each subagent for a report: mission, what is done and checked, current step, files touched, what is left. An agent that stays silent for 5 minutes is stopped, and its record is rebuilt from its log (`/stop-all 10` waits 10 minutes). Everything is written to `.ia/resume.md` at the repository root, otherwise in the project folder, otherwise on the Desktop. The `.ia/` folder stays out of git. No commit, no push.

## /resume-all

Claude finds the latest `resume.md`, checks that nothing has moved since the stop (branch, agents' files) and asks you what to do if something changed. It then relaunches each unfinished agent with the same type. The file is never deleted: it moves to the `RESUMED` state.

## What is in the folder

`SKILL.md` holds the procedure. `report-request.md`, `resume-template.md` and `relaunch-brief.md` are the message sent to the agents, the template of `resume.md` and the brief of the relaunched agents. `scripts` summarises the agents' logs, finds the resume files and checks that a `resume.md` is complete. `tests` covers the pure parts of these scripts.
