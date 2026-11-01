# finishing-a-development-branch

Une skill et une commande pour Claude Code, qui terminent proprement une branche de travail finie. Pour
l'installer, voir `INSTALL.md` à la racine du dépôt.

## /finir

Tape `/finir` quand une fonction ou un correctif est fini. Claude regarde d'abord l'état de la branche : son
dossier de travail, la branche d'origine, les commits à intégrer, ce qui est déjà poussé, les fichiers
oubliés. Il lance ensuite les tests du projet, et s'arrête s'ils échouent. Un test qui échoue une fois puis
passe compte comme un échec.

Quand tout est vert, il te pose une seule question avec quatre choix, la recommandation en premier :
pousser et ouvrir une pull request, fusionner dans la branche d'origine sur cette machine, garder la branche telle
quelle, ou supprimer le travail. Le choix de supprimer liste dans la question les commits et les fichiers
qui seraient perdus. Rien ne part sans ta réponse.

On peut préciser : `/finir remise` termine la branche ou le dossier de travail nommé.

## Ce qui se passe après le choix

La fusion se fait sans rien lire sur GitHub, les tests repassent sur le résultat, puis le dossier de travail
et la branche sont retirés. Le push passe par `push.py` de clean-commits, et la pull request par la skill
account-keys quand elle est installée, sinon avec tes propres identifiants git. Rien n'est jamais forcé.
Le texte de la pull request suit le modèle du dépôt quand il en a un, sinon c'est quelques phrases dans la
langue du dépôt, sans mention d'un outil d'IA, même si un fichier CONTRIBUTING en réclame une.

Avant tout départ, les commits pas encore poussés qui portent une signature d'IA sont nettoyés par
clean-commits. Un commit déjà poussé est signalé, jamais réécrit.

## Le nettoyage

Un dossier de travail ne part que si `state.py` dit qu'il peut partir : travail fusionné ou poussé, rien
de non commité, et dossier créé par la skill using-git-worktrees. Les fichiers de `.ia/` qu'il contient sont d'abord copiés dans le dépôt principal. Les
fichiers temporaires sont supprimés, les serveurs lancés pendant la tâche sont arrêtés, aucun sous-agent ne
reste en route. Le dossier `.ia/` reste et n'est jamais commité.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `scripts/state.py` lit l'état de la branche et dit si le dossier
de travail peut partir, `tests/test_pure.py` vérifie ses décisions (lancer
`python -I -m unittest discover -s tests -p "test_*.py"` depuis le dossier). `reference/pull-request.md`
décrit le corps de la pull request et les commandes. `commands` contient la commande `/finir`.
