# clean-commits

Une skill et une commande pour Claude Code, qui font des commits propres dans n'importe quel dépôt.
Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /commit

Tape `/commit` quand le travail de la session est prêt. Claude regarde l'état du dépôt, puis ne
prend que les fichiers qu'il a lui-même créés, modifiés ou supprimés pendant la session. Si
d'autres fichiers ont bougé, il pose une seule question : les laisser à l'autre session, les
inclure, ou choisir un par un. Il range ensuite les changements par intention, un commit pour
chacune, et pousse la branche.

On peut préciser : `/commit le panier` ne prend que ce qui touche au panier.

Le message suit l'historique du dépôt. Un dépôt écrit en français reçoit des messages en français,
un dépôt en `feat(scope): ...` garde cette forme, avec ses propres types et ses propres scopes.
S'il n'y a encore aucun commit, Claude demande la langue.

Avant chaque commit, il lance le linter et la vérification de types du projet sur les fichiers du
commit, s'ils existent. Une erreur dans ces fichiers bloque le commit. Une erreur ailleurs ne
bloque rien, elle est signalée. La suite de tests complète reste au travail d'avant.

Le push passe par l'outil de comptes que désigne la variable `CLAUDE_SKILLS_ACCOUNTS` quand elle est
définie (par exemple l'outil de la skill account-keys), sinon par un `git push` simple avec tes propres
identifiants. Un push refusé n'est jamais forcé.

## Quand une autre skill l'appelle

clean-code appelle clean-commits à la fin de chaque étape de son plan, avec la liste exacte des
fichiers de l'étape. Dans ce cas il n'y a ni question sur les autres fichiers, ni push : les
commits restent en local.

## Ce qui ne passe jamais

Aucune signature d'outil d'IA dans un message, qu'il s'agisse de Claude, Codex, Copilot, Cursor,
Gemini, Jules, Devin ou Aider : un trailer `Co-Authored-By` vers l'un d'eux, une ligne
`Made-with: Cursor` ou un lien de session sont refusés, et s'il en traîne un dans un commit pas
encore poussé, il est retiré. Un co-auteur qui est une personne reste, même s'il s'appelle Claude.
La liste complète vient de la skill `anti-empreinte`. Dans un commit déjà poussé,
Claude le signale et ne réécrit rien. Les fichiers de secrets, les sorties de build, les dossiers
`.ia/` et `.claude/` ne partent jamais. Aucun `git add .`, aucun `--no-verify`, aucun push forcé,
aucun stash du travail d'une autre session.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. Le dossier `scripts` contient cinq outils :
`state.py` lit l'état du dépôt, `scrub.py` retire l'attribution des commits pas encore poussés,
`checks.py` lance les vérifications rapides, `commit.py` vérifie le message et les fichiers puis
commite, `push.py` pousse. `scripts/lib` contient ce qu'ils partagent. `commands` contient la
commande `/commit`.
