---
description: Commite proprement les fichiers de cette session, un commit par intention, puis pousse la branche.
argument-hint: "[fichiers, dossier ou intention a commiter]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion
---

Charger la skill `clean-commits` avec le tool `Skill` et suivre sa partie Procedure, etape par
etape, en mode `/commit`. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/clean-commits/SKILL.md`, ou `~/.claude/skills/clean-commits/SKILL.md`
quand la variable est vide, et l'appliquer pareil.

Precision donnee : $ARGUMENTS. Si elle n'est pas vide, elle restreint les fichiers ou oriente le
message, sans jamais ajouter un fichier qu'une autre session a modifie sans poser la question.

Les fichiers de cette session partent dans les commits. Les autres fichiers modifies font l'objet
d'une seule question avec `AskUserQuestion`. Sans historique dans le depot, demander la langue des
messages. Le push passe par `push.py`, jamais par un `git push` direct.

Reponse finale en francais, courte : chaque commit avec son hash et son titre, le resultat du push,
les fichiers laisses de cote et pourquoi.
