---
description: Ecrit des tests qui tournent sur le vrai code et peuvent echouer pour la bonne raison, puis le code qui les fait passer.
argument-hint: "[comportement a ajouter, bug a corriger ou fichier a couvrir]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion
---

Charger la skill `test-driven-development` avec le tool `Skill` et suivre ses regles. Si le tool `Skill`
ne la trouve pas, lire directement `$CLAUDE_CONFIG_DIR/skills/test-driven-development/SKILL.md`, ou
`~/.claude/skills/test-driven-development/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Demande donnee : $ARGUMENTS.

- Un comportement a ajouter : le test, puis le code, et la verification par casse imaginee decrite dans la
  skill.
- Un bug : d'abord le test qui le reproduit et echoue sur le code non corrige, ensuite seulement la
  correction.
- Un fichier deja ecrit sans tests : des tests prouves chacun par une casse volontaire, remise par une
  modification, sans rien supprimer du code existant.
- Vide : demander ce qu'il faut construire, en une seule question avec `AskUserQuestion`.

Une regle que la demande laisse ouverte (arrondi, limite, cas d'erreur) se demande avant le premier
test, jamais devinee. Les tests passent par `scripts/run.py` de la skill : le test seul, puis son
fichier, puis la suite complete a la fin.

Reponse finale en francais, courte : les comportements couverts (pour un bug, la ligne d'echec sur le
code non corrige), le resultat de la suite complete et chaque echec nomme, les tests ecrits apres coup
et comment ils ont ete prouves, le commit s'il y en a un.
