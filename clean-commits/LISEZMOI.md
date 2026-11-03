# clean-commits

Une skill et une commande pour Claude Code qui font des commits propres dans n'importe quel dépôt. Installation : voir `INSTALL.md` à la racine du dépôt.

## /commit

Tape `/commit` quand le travail est prêt. Claude ne prend que les fichiers qu'il a lui-même créés, modifiés ou supprimés pendant la session. Si d'autres fichiers ont bougé, il pose une seule question : les laisser, les inclure, ou choisir un par un. Il range ensuite les changements par intention, un commit chacune, puis pousse la branche. `/commit le panier` restreint à ce qui touche au panier.

Le message suit l'historique : langue du dépôt, et forme `feat(scope): ...` seulement si le dépôt l'utilise. Sans historique, Claude demande la langue. Avant chaque commit, le linter et la vérification de types du projet tournent sur les fichiers du commit : une erreur dans ces fichiers bloque, une erreur ailleurs est seulement signalée.

## Le push

Si la variable `CLAUDE_SKILLS_ACCOUNTS` désigne un outil de comptes, le push GitHub passe par lui. Sinon c'est un `git push` simple avec tes identifiants, sans jamais ouvrir de fenêtre de connexion. Un push refusé n'est jamais forcé.

## Appel par une autre skill

clean-code appelle clean-commits à la fin de chaque étape avec la liste exacte des fichiers : pas de question, pas de push.

## Ce qui ne passe jamais

Aucune signature d'outil d'IA dans un message (Claude, Codex, Copilot, Cursor, Gemini, Jules, Devin, Aider) : elle est refusée, et retirée si elle traîne dans un commit pas encore poussé. Dans un commit déjà poussé, Claude le signale sans rien réécrire. Les fichiers de secrets, les sorties de build et les dossiers `.ia/` et `.claude/` ne partent jamais. Aucun `git add .`, `--no-verify`, push forcé ni stash du travail d'une autre session.

## Le dossier

`SKILL.md` porte la procédure. `scripts` : `state.py` lit l'état, `scrub.py` retire l'attribution des commits non poussés, `checks.py` lance les vérifications rapides, `commit.py` vérifie puis commite, `push.py` pousse. `commands` contient `/commit`.
