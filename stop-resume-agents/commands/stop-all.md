---
description: Arrete tout, sous-agents compris, et ecrit .ia/resume.md avec le compte rendu de chacun.
argument-hint: "[raison] [delai d'attente en minutes]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,ScheduleWakeup,CronList,CronDelete,AskUserQuestion
---

Arguments : $ARGUMENTS. Un nombre seul est le delai d'attente en minutes (5 par defaut), le reste est la raison.

Charger la skill `stop-resume-agents` avec le tool `Skill` et appliquer sa partie /stop-all.

Reponse finale en trois ou quatre lignes en francais, puis attendre.
