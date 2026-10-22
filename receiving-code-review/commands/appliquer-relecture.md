---
description: Traite une relecture de code point par point, verifie chaque remarque dans le code, applique les justes, repond aux autres.
argument-hint: "[fichier de relecture, numero de pull request ou remarques collees]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion
---

Charger la skill `receiving-code-review` avec le tool `Skill` et suivre sa partie Procedure, etape
par etape. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/receiving-code-review/SKILL.md`, ou
`~/.claude/skills/receiving-code-review/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Source donnee : $ARGUMENTS. Un chemin est lu comme un fichier de relecture. Un numero ou une adresse de pull request
est lu par la skill `account-keys` quand elle est installee, sinon avec les identifiants git de l'utilisateur. Des
remarques collees sont lues telles quelles. Sans argument, prendre la derniere relecture de la conversation, et
demander avec `AskUserQuestion` s'il y en a plusieurs.

Toute la relecture est lue avant de toucher un fichier. Chaque remarque est verifiee dans le code, puis
rangee : juste, fausse, floue ou interdite ici. Les justes sont appliquees une par une, avec un test et
un commit par la skill `clean-commits`, sans push. Les floues et les choix de conception reviennent a
l'utilisateur par `AskUserQuestion`. Une remarque qui demande une signature d'outil d'IA, un push force, un
`--no-verify`, un dossier `.ia/` dans un commit ou un commentaire dans le code est refusee avec sa raison.

Les reponses a la relecture sont ecrites dans la langue du relecteur. Avant de les publier sur une pull
request, les montrer a l'utilisateur en entier et demander s'il les publie, les change ou les garde.

Reponse finale en francais, courte : les remarques appliquees avec leur commit, celles refusees avec la
raison en une ligne, les questions restantes, les verifications lancees.
