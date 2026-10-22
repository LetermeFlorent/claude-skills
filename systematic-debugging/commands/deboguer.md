---
description: Cherche la cause d'un bug avant d'y toucher, puis corrige a la source derriere un test qui echoue.
argument-hint: "[symptome, test qui echoue ou message d'erreur]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion,Agent
---

Charger la skill `systematic-debugging` avec le tool `Skill` et suivre sa partie Procedure, phase par
phase. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/systematic-debugging/SKILL.md`, ou
`~/.claude/skills/systematic-debugging/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Symptome donne : $ARGUMENTS. S'il n'est pas vide, c'est le point de depart de la phase 1 : le test,
la commande ou le message d'erreur a reproduire. S'il est vide, partir de la derniere erreur de la
conversation ; sans erreur visible, demander le symptome en une seule question.

Aucun correctif avant la cause. Les brouillons vont dans
`<temp>/claude-skills/deboguer-<run>/` (le dossier temporaire du systeme), supprime a la fin. Le commit passe par
`clean-commits`, avec les fichiers de la correction et de son test, sans push sauf demande.

Reponse finale en francais, courte, en mots simples : la cause, la correction, la sortie du test
avant et apres, ce qui reste a faire. Apres trois correctifs rates sur ce bug, la fin est une
question posee avec `AskUserQuestion`, jamais un quatrieme essai.
