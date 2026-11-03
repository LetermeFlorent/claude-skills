---
description: Stop everything, subagents included, and write .ia/resume.md with each one's report.
argument-hint: "[reason] [wait delay in minutes]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,ScheduleWakeup,CronList,CronDelete,AskUserQuestion
---

Arguments: $ARGUMENTS. A lone number is the wait delay in minutes (5 by default), the rest is the reason.

Load the `stop-resume-agents` skill with the `Skill` tool and apply its /stop-all part.

Final answer in three or four lines in the user's language, then wait.
