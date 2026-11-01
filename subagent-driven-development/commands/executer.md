---
description: Execute un plan tache par tache avec un sous-agent par tache, une relecture apres chacune et un commit par tache.
argument-hint: "[chemin du plan, ou numero de tache]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,SendMessage,AskUserQuestion
---

Charger la skill `subagent-driven-development` avec le tool `Skill` et suivre sa partie Procedure,
etape par etape. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/subagent-driven-development/SKILL.md`, ou
`~/.claude/skills/subagent-driven-development/SKILL.md` quand la variable est vide, et l'appliquer
pareil.

Precision donnee : $ARGUMENTS. Un chemin designe le plan a executer. Un numero de tache limite le
travail a cette tache, les autres restent pour plus tard. Vide : le plan le plus recent de
`.ia/plans/` du depot. Une execution deja commencee reprend la ou le journal s'arrete, sans refaire
une tache commitee.

Reponse finale en francais, courte, comme l'etape 5 de la skill le dit.
