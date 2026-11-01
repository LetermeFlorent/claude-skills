---
description: Passe une demande au grill avant tout code, puis rend un petit design ou une spec selon sa taille.
argument-hint: "[ce qu'il faut concevoir ou changer]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion,Agent
---

Charger la skill `brainstorming` avec le tool `Skill` et suivre ses etapes dans l'ordre. Si le tool
`Skill` ne la trouve pas, lire directement `$CLAUDE_CONFIG_DIR/skills/brainstorming/SKILL.md`, ou
`~/.claude/skills/brainstorming/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Demande : $ARGUMENTS. C'est le sujet du grill. Si elle est vide, demander en une seule question
ouverte ce qu'il faut concevoir, et rien d'autre.

Reponse finale en francais, courte : la taille lue, la phrase qui dit ce qui va etre construit et
pourquoi, le chemin de la spec quand il y en a une, puis la suite qui demarre (le plan avec
`/planifier`, ou le changement lui-meme).
