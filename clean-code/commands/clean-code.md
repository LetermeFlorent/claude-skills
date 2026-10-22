---
description: Audite une portee contre les regles de clean code, rend une note sur 20, puis demande quoi corriger.
argument-hint: "[portee : dossier, application ou fichier]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,ToolSearch,Agent,AskUserQuestion,SendMessage,ListAgents
---

Audit en lecture seule jusqu'a la reponse a la question de dose. Aucun fichier du projet ne bouge
avant.

Portee demandee : $ARGUMENTS. Si c'est vide, demander la portee avec `AskUserQuestion`, en
proposant le projet entier puis chaque application ou dossier de premier niveau qui existe
vraiment, du plus etroit au plus large.

Charger la skill `clean-code` avec le tool `Skill` et suivre ses parties Audit puis Apply, etape
par etape, sans en sauter une. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/clean-code/SKILL.md`, ou `~/.claude/skills/clean-code/SKILL.md` quand
la variable est vide, et l'appliquer pareil.

Reponse finale en francais, courte : la note avant et apres, les etapes faites avec leur commit,
ce qui reste et pourquoi. Pas de push.
