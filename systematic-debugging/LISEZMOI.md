# systematic-debugging

Une skill et une commande pour Claude Code, qui cherchent la cause d'un bug avant d'y toucher.
Elle reprend la skill du même nom de superpowers, réécrite. Pour l'installer, voir `INSTALL.md` à la
racine du dépôt.

## /deboguer

Tape `/deboguer` quand un test plante, qu'un build casse ou qu'un programme fait autre chose que
prévu. Le symptôme peut suivre la commande : `/deboguer test_service plante sur un timeout`, ou le
message d'erreur collé tel quel. Sans rien derrière, Claude part de la dernière erreur de la
conversation, et te demande le symptôme s'il n'en voit aucune.

## Comment il s'y prend

Trois étapes, dans l'ordre. D'abord la cause : reproduire le bug avec la plus petite commande, regarder
ce qui a changé, remonter la valeur fautive jusqu'à son origine. Ensuite la comparaison avec du code qui
marche, et une hypothèse à la fois, testée par le plus petit changement possible. Enfin la correction,
derrière un test qui échoue d'abord, en un seul changement à la source, et la suite de tests relancée puis
lue.

Il compte les correctifs ratés sur le même bug, ceux déjà dans l'historique compris. Au troisième,
il s'arrête : c'est la conception qui est en cause, et il te pose la question avec deux à quatre
choix plutôt que de tenter un quatrième correctif.

Un `sleep` ou une relance ne corrige rien, ça cache. Dans les tests, il attend une condition ; en
dehors, une ligne de log, avec une boucle bornée. Quand la prod est en panne, il peut te proposer
de remettre la dernière version qui marchait pendant qu'il cherche. C'est toi qui décides, puisque
ça part sous ton nom.

## Avec les autres skills

Le test qui échoue passe par `test-driven-development`, la preuve que c'est réparé par
`verification-before-completion`. Le code suit `clean-code` et le texte suit `anti-empreinte`. Le
commit passe par `clean-commits`, avec les seuls fichiers de la correction et de son test, sans
push : le push n'a lieu que si tu le demandes. Un bug dans une page web se reproduit par
`chrome-bidi`, sans fenêtre à l'écran. Quand le bug a demandé plusieurs essais, la leçon est écrite
tout de suite en skill, dans le projet si elle le concerne, dans `~/.claude/skills` sinon.

## Ce qui ne passe jamais

Un correctif attend toujours la cause. Les scripts de reproduction, les logs et les captures vivent
dans `<temp>/claude-skills/deboguer-<run>/` (`<temp>` est le dossier temporaire du système)
et partent à la fin, jamais dans le dépôt. Les lignes de debug sont retirées avant le commit. Pas de
`--no-verify`, de `git add .` ni de mention d'IA dans un commit, même quand un fichier CONTRIBUTING le
réclame. Un sous-agent ne reconstruit jamais un conteneur partagé, et la session principale ne le fait
pas par-dessus le build d'une autre session.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `reference` contient trois fiches : remonter une valeur
jusqu'à sa source, ajouter un contrôle à chaque couche traversée, attendre une condition plutôt
qu'une durée. `scripts/find_polluter.py` trouve le test qui laisse un fichier derrière lui ou qui en
casse un autre, en coupant la liste en deux jusqu'à n'en garder qu'un. Il remplace le script bash
d'origine, qui ne savait lancer que `npm test`. `scripts/lib` contient la recherche et le lancement
des commandes, `tests` ses tests unitaires, `commands` la commande `/deboguer`.
