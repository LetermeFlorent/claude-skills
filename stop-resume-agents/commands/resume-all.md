---
description: Resume the work stopped by /stop-all and relaunch each subagent with its context.
argument-hint: "[path to resume.md]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,Agent,AskUserQuestion,CronList,CronCreate,ScheduleWakeup
---

Arguments: $ARGUMENTS. A given path is the file to resume from.

Load the `stop-resume-agents` skill with the `Skill` tool and apply its /resume-all part.

Answer in three or four lines in the user's language, then carry on with your own share of the work.
