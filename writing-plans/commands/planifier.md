---
description: Transforme une specification terminee en plan de taches, test d'abord, un commit par tache, range dans .ia/plans.
argument-hint: "[chemin de la specification ou quelques mots qui la designent]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,AskUserQuestion
---

Charger la skill `writing-plans` avec le tool `Skill` et suivre sa partie Procedure, etape par etape. Si le
tool `Skill` ne la trouve pas, lire directement `$CLAUDE_CONFIG_DIR/skills/writing-plans/SKILL.md`, ou
`~/.claude/skills/writing-plans/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Precision donnee : $ARGUMENTS. Si elle designe une specification, c'est l'entree du plan. Si elle est vide,
prendre la plus recente du dossier `.ia/specs/` du depot, et poser une seule question avec `AskUserQuestion`
quand deux se valent. Sans aucune specification, ne rien ecrire et proposer `/concevoir`.

Le plan va dans `.ia/plans/`, jamais ailleurs, et ne part dans aucun commit sauf demande de l'utilisateur dans cette
conversation. Aucun fichier du projet n'est touche en dehors du plan. Avant de conclure, lancer `plan_lint.py`
et la relecture par le sous-agent, et lire leurs sorties.

Reponse finale courte, dans la langue de l'utilisateur : le chemin du plan, le nombre de taches,
le resultat du controle et de la relecture, la methode choisie pour la suite avec la commande a taper.
Une decision qui lui revient se pose avant la derniere ligne, pas en liste d'attente.
