---
description: Reprend le travail arrete par /stop-all et relance chaque sous-agent avec son contexte.
argument-hint: "[chemin du resume.md]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,Agent,AskUserQuestion,CronList,CronCreate,ScheduleWakeup
---

Arguments : $ARGUMENTS. Un chemin donne est le fichier a reprendre.

Charger la skill `stop-resume-agents` avec le tool `Skill` et appliquer sa partie /resume-all.

Reponse en trois ou quatre lignes en francais, puis continuer sa propre part du travail.
