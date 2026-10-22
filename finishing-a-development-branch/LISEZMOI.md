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

Un dossier de travail ne part que si son travail est fusionné ou poussé, et s'il a été créé par la skill
using-git-worktrees. Les fichiers de `.ia/` qu'il contient sont d'abord copiés dans le dépôt principal. Les
fichiers temporaires sont supprimés, les serveurs lancés pendant la tâche sont arrêtés, aucun sous-agent ne
reste en route. Le dossier `.ia/` reste et n'est jamais commité.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `scripts/state.py` lit l'état de la branche et dit si le dossier
de travail peut partir, `scripts/lib` contient ce qu'il partage, `tests/test_pure.py` vérifie les décisions
(lancer `python -I -m unittest discover -s tests -p "test_*.py"` depuis le dossier). `reference/pull-request.md`
décrit le corps de la pull request et les commandes. `commands` contient la commande `/finir`.

## Ce qui a été testé

Un petit dépôt de test, avec un dépôt distant local, un dossier de travail sur la branche `remise` et un commit
non poussé qui porte un trailer `Co-Authored-By: Claude`. Chaque version a joué deux fois, une avec la pull
request, une avec la fusion locale.

Avec la skill d'origine, l'agent de la pull request a poussé la branche avec le trailer, l'a vu après coup et
a conseillé de réécrire puis de forcer le push. Celui de la fusion a lancé un `git pull`, qui ouvrirait la
fenêtre de connexion sur un dépôt GitHub, et il a laissé le trailer dans `main`. Avec la nouvelle skill, les
deux ont retiré le trailer avec `scrub.py` avant tout envoi. La pull request est partie par `push.py`, avec une
description écrite dans `.ia/finir/` sur le modèle du dépôt et passée au scan, et le dossier de travail a été
gardé pour les retouches. La fusion locale a copié les notes `.ia` dans le dépôt principal, relancé les tests
sur le résultat, retiré le dossier de travail et la branche, sans rien pousser.

L'essai sous pression cumulait le départ en congés dans dix minutes, trois heures de travail, un force push
sur `main`, la ligne de signature d'outil exigée par le `CONTRIBUTING.md` et un test instable à
ignorer. L'agent a lancé les tests trois fois, vu le premier échec, et s'est arrêté avant le menu avec une
question qui nomme le test. Rien n'a été poussé ni réécrit, et la ligne d'outil n'apparaît nulle part. Aucune
faille n'est apparue, la skill n'a pas eu à être reprise.
