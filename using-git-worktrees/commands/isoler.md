---
description: Cree un worktree git isole sur sa propre branche, puis lance les tests de depart.
argument-hint: "[tache en quelques mots, branche de depart optionnelle]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion,EnterWorktree
---

Precision : $ARGUMENTS. Elle donne la tache (donc la branche et le dossier) et une branche de depart si elle
en cite une. Vide : partir de la conversation, et poser une seule question si la tache reste inconnue.

Charger la skill `using-git-worktrees` avec le tool `Skill` et suivre sa procedure.

Reponse finale en francais, courte : chemin, branche et depart, modifications restees dans le dossier
d'origine, resultat des tests de depart.
