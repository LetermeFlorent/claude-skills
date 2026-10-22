---
description: Mene un projet de l'idee a la fin en enchainant les skills, images de reference comprises.
argument-hint: "[le projet a lancer, ou rien pour reprendre celui du dossier]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion,Agent,SendMessage
---

Charger la skill `project-dev` avec le tool `Skill` et suivre ses etapes dans l'ordre. Si le tool
`Skill` ne la trouve pas, lire directement `$CLAUDE_CONFIG_DIR/skills/project-dev/SKILL.md`, ou
`~/.claude/skills/project-dev/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Demande : $ARGUMENTS. Si elle est vide et que le dossier courant a un `.ia/`, reprendre le projet la
ou le disque dit qu'il s'est arrete. Sinon, demander en une seule question ouverte quel projet lancer.

La premiere question d'un projet est toujours "As-tu des images de reference ?". Les images sont
copiees dans `.ia/references/` du projet, jamais commitees. Rien n'est construit avant l'accord sur
la spec puis sur le plan, et rien n'est dit fini avant la comparaison d'une capture avec les images.

Reponse finale en francais, courte : l'etape atteinte, les images utilisees, ce qui a ete compare,
puis la question de l'etape suivante.
