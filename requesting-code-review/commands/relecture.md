---
description: Fait relire une serie de commits par un relecteur neuf, qui rend des remarques avec fichier, ligne et correction.
argument-hint: "[plage : base..tete, branche, numero de PR ou tache a relire]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,Agent,SendMessage,AskUserQuestion
---

Charger la skill `requesting-code-review` avec le tool `Skill` et suivre sa partie Procedure, etape
par etape. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/requesting-code-review/SKILL.md`, ou
`~/.claude/skills/requesting-code-review/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Precision donnee : $ARGUMENTS. Vide : relire les commits de la branche courante depuis son point de
depart. Deux references separees par `..` fixent la base et la tete. Un numero de PR ou une tache
designe l'exigence a donner au relecteur, pas une autorisation de publier.

La relecture est faite par un sous-agent, jamais en direct, meme pour un petit changement ou une PR deja approuvee.
Rien ne part sur GitHub sans demande de l'utilisateur, et alors par la skill account-keys quand elle est installee,
sinon avec ses propres identifiants git. Une question seulement si deux lectures de la demande donnent un code
different, avec `AskUserQuestion`.

Reponse finale en francais, courte : le verdict, le nombre de remarques par gravite, les une ou deux
qui comptent vraiment, le chemin de la note si elle est gardee, et la suite (`/appliquer-relecture`).
