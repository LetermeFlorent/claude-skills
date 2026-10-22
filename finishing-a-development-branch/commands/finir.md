---
description: Termine une branche de travail finie : verifie les tests, propose fusion locale, pull request, garde ou suppression, puis nettoie.
argument-hint: "[branche ou dossier de travail a terminer]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,AskUserQuestion
---

Charger la skill `finishing-a-development-branch` avec le tool `Skill` et suivre sa partie Procedure,
etape par etape. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/finishing-a-development-branch/SKILL.md`, ou
`~/.claude/skills/finishing-a-development-branch/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Precision donnee : $ARGUMENTS. Si elle n'est pas vide, c'est la branche ou le dossier de travail a
terminer : lancer `state.py` depuis ce dossier. Si elle est vide, prendre le dossier courant. Elle ne change
jamais le choix de l'utilisateur : fusion, pull request, garde ou suppression se demandent toujours avec
`AskUserQuestion`, la recommandation en premier.

Les tests passent avant la question, et se relisent apres une fusion. Le push passe par `push.py` de clean-commits, la
pull request par la skill account-keys quand elle est installee, sinon avec les identifiants git de l'utilisateur,
jamais par un `git push` direct, et jamais de force. Le corps de la pull request suit le modele du depot et n'a aucune
mention d'outil d'IA. La suppression du travail liste ce qui sera perdu dans la question.

Reponse finale en francais, courte : le choix fait, ce qui a bouge (branche fusionnee, adresse de la pull
request, chemin garde, commits supprimes), ce qui a ete nettoye, ce qui est laisse et pourquoi.
