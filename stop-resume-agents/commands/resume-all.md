---
description: Reprend le travail arrete par /stop-all et relance chaque sous-agent avec son contexte de resume.md.
argument-hint: "[chemin du resume.md]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,Agent,AskUserQuestion,CronList,CronCreate,ScheduleWakeup
---

Reprise du travail arrete par /stop-all.

Arguments du user : $ARGUMENTS (aucun si vide). Un chemin donne est le fichier a reprendre.

Charger la skill `stop-resume-agents` avec le tool `Skill` et appliquer sa partie /resume-all,
etape par etape, sans en sauter une. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/stop-resume-agents/SKILL.md`, ou `~/.claude/skills/stop-resume-agents/SKILL.md`
quand la variable est vide, et l'appliquer pareil.

Ne jamais supprimer le fichier de reprise. Ne rien refaire de ce qui est marque termine.
Reponse en trois ou quatre lignes en francais, puis continuer sa propre part du travail.
