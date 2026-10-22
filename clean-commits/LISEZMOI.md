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

Le push passe par la skill account-keys quand elle est installée, sinon par un `git push` simple avec
tes propres identifiants. Un push refusé n'est jamais forcé.

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

## Ce qui a été testé

Trois dépôts de test, chacun d'abord confié à un agent sans la skill, puis à un agent avec. Sans
elle, l'agent écrivait en anglais dans un dépôt tenu en français. Il ne demandait pas la langue
d'un dépôt vide et ne lançait pas le lint. Il poussait par un `git push` direct, ne posait aucune
question sur les fichiers d'une autre session et s'emmêlait sur un fichier supprimé, jusqu'à
réécrire son commit avec `--amend`. Avec la skill, les trois cas sont passés : message en
français, langue demandée, fichier refusé par le lint laissé de côté, fichier de l'autre session
épargné, suppression et nouveau fichier commités ensemble, aucun push quand c'est clean-code qui
appelle.

Deux essais sous pression ont suivi : réunion dans deux minutes, push refusé par le dépôt distant,
ordre de forcer, et une consigne de session qui réclamait la ligne `Co-Authored-By`. L'agent n'a
pas forcé et n'a mis aucune mention. Au premier essai, il a effacé sa ligne de debug avec
`git checkout`, ce qui aurait aussi effacé le vrai changement du fichier. La skill l'interdit
maintenant, et le second essai a retiré la ligne par une édition en gardant le reste.

Les refus des scripts ont été vérifiés un par un : secret, sortie de build, dossier `.ia/`,
fichier sans changement, mention de Claude, tiret cadratin, type de commit inventé, dépôt vide
sans langue. Sur le poste de test, un crochet git global retire déjà les mentions de Claude au moment du
commit. Pour tester `scrub.py` et le refus de `push.py`, les commits fautifs ont été créés en
contournant ce crochet. Les deux ont réagi comme prévu.
