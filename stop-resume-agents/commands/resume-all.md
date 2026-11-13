---
description: Resume the work stopped by /stop-all and relaunch each subagent with its context.
argument-hint: "[path to resume.md]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,Monitor,Agent,AskUserQuestion,CronList,CronCreate,ScheduleWakeup
---

Arguments: $ARGUMENTS. Given path = file to resume from.

Load `stop-resume-agents` skill with `Skill` tool, apply its /resume-all part.

Answer in three or four lines in user's language, then carry on with own share of work.
