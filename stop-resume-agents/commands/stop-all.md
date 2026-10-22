---
description: Arrete tout, sous-agents compris, demande a chacun un compte rendu complet et ecrit .ia/resume.md dans le projet.
argument-hint: "[raison] [delai d'attente en minutes]"
allowed-tools: Read,Write,Edit,Bash,Skill,ToolSearch,ListAgents,SendMessage,TaskStop,ScheduleWakeup,CronList,CronDelete,AskUserQuestion
---

Arret immediat. Aucune nouvelle etape, aucune derniere verification. Seul un fichier a moitie ecrit
est termine, pour ne rien laisser casse.

Arguments du user : $ARGUMENTS (aucun si vide). Un nombre seul est le delai d'attente des
comptes rendus en minutes, 5 par defaut. Le reste est la raison, elle ne change rien a la procedure.

Charger la skill `stop-resume-agents` avec le tool `Skill` et appliquer sa partie /stop-all, etape
par etape, sans en sauter une. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/stop-resume-agents/SKILL.md`, ou `~/.claude/skills/stop-resume-agents/SKILL.md`
quand la variable est vide, et l'appliquer pareil.

Pas de commit, pas de push. Reponse finale en trois ou quatre lignes en francais, puis attendre.
