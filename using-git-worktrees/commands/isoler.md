---
description: Cree un espace de travail isole (worktree git) sur sa propre branche, par defaut dans le dossier `.ia/worktrees` du depot, puis lance les tests de depart.
argument-hint: "[tache en quelques mots, branche de depart optionnelle]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion,EnterWorktree
---

Charger la skill `using-git-worktrees` avec le tool `Skill` et suivre sa partie Procedure, etape
par etape. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/using-git-worktrees/SKILL.md`, ou `~/.claude/skills/using-git-worktrees/SKILL.md`
quand la variable est vide, et l'appliquer pareil.

Precision donnee : $ARGUMENTS. Si elle n'est pas vide, elle donne la tache, donc le nom de la
branche et du dossier, et une branche de depart si elle en cite une. Vide, partir de la
conversation en cours ; si rien n'indique la tache, poser une seule question.

Taper la commande vaut demande d'isolation : ne pas redemander si l'utilisateur veut un worktree. Les
regles de la skill valent telles quelles (dossier, nom de branche, aucun fetch direct, tests de depart
en priorite basse, aucune suppression sans accord).

Reponse finale en francais, courte : le chemin du worktree, la branche et son point de depart,
combien de modifications sont restees dans le dossier d'origine, le resultat des tests de depart
en une ligne.
