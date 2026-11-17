---
description: Stop everything, subagents included, and write .ia/resume.md with each one's report.
argument-hint: "[force|wait] [reason] [wait delay in minutes]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,Monitor,ScheduleWakeup,CronList,CronDelete,AskUserQuestion
---

Arguments: $ARGUMENTS. `force` or `wait` = close mode, asked when absent and a subagent runs.
Lone number = wait delay in minutes (5 by default, 30 at most), rest = reason.

Load `stop-resume-agents` skill with `Skill` tool, apply its /stop-all part.

Final answer in three or four lines in user's language, then wait.
