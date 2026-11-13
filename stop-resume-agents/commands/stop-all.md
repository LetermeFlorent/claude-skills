---
description: Stop everything, subagents included, and write .ia/resume.md with each one's report.
argument-hint: "[reason] [wait delay in minutes]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,Monitor,ScheduleWakeup,CronList,CronDelete,AskUserQuestion
---

Arguments: $ARGUMENTS. Lone number = wait delay in minutes (5 by default, 30 at most), rest = reason.

Load `stop-resume-agents` skill with `Skill` tool, apply its /stop-all part.

Final answer in three or four lines in user's language, then wait.
