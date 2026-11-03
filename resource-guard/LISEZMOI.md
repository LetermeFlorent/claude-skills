# resource-guard

Plusieurs agents travaillent en même temps sur le même PC. Quand l'un lance une compilation, des tests ou
docker pendant qu'un autre fait pareil, tout rame. Cette skill fait attendre l'agent tant que la machine
n'a pas assez de place. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## Ce qui se passe

Avant chaque commande, l'agent regarde si elle est lourde : une compilation, des tests, docker, un serveur
de développement, une installation de paquets. Une commande légère (`git status`, `ls`) passe tout de suite,
sans rien mesurer. Une commande lourde attend qu'il reste au moins 1,5 Go de mémoire libre, que le
processeur tourne à moins de 85 % et que le disque ne soit pas saturé. Au bout de 5 minutes sans place, la
commande n'est pas lancée et l'agent reçoit la raison.

Il manque de la place sur le disque C: (moins de 20 Go) ? Un simple avertissement s'affiche, sans attente.
Attendre ne libère pas le disque, il faut faire le ménage.

## À la main

`python -I "<dossier>/scripts/guard.py" check` affiche une ligne d'état et dit si c'est bon. `wait` attend
que ça le devienne. Les seuils se changent avec des options ou des variables d'environnement, listées dans
`SKILL.md`.

## Avec quel agent

Avec Claude Code, l'installateur du dépôt branche le contrôle tout seul. Codex CLI et Qwen Code ont le même
genre de crochet : `SKILL.md` donne les lignes à coller dans leur configuration. Pour Gemini CLI et les
autres, une phrase dans leur fichier d'instructions leur demande de lancer `wait` avant une commande lourde.

## Le contenu du dossier

`scripts/guard.py` est l'outil. `scripts/lib` contient la liste des commandes lourdes, la lecture de
l'événement reçu, les seuils et la mesure, avec un fichier par système (Windows, Linux, macOS).
`tests/test_pure.py` vérifie la liste, les seuils et lance une vraie mesure.
