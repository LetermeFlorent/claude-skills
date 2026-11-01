# requesting-code-review

Une skill et une commande pour Claude Code, qui font relire un travail fini par un relecteur neuf
avant de passer à la suite ou de fusionner. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /relecture

Tape `/relecture` quand une tâche, une fonctionnalité ou une branche est terminée. Claude cherche la
série de commits à relire (de l'endroit où la branche a quitté `main` jusqu'au dernier commit), retrouve
ce que le travail devait faire, puis envoie un sous-agent relecteur qui ne connaît rien de la session.
Le relecteur est en lecture seule : il ne modifie rien, ne lance aucun build et ne fait appel à
personne d'autre.

On peut préciser : `/relecture abc123..def456` fixe la plage, `/relecture la tâche 3 du plan` dit
quelle exigence servira de mesure.

## Ce que la relecture contrôle

Le relecteur contrôle cinq choses dans l'ordre : que le code fait ce qui était demandé, sans erreur
sur les cas réels ; les règles de clean-code sur les lignes changées (taille, commentaires, noms
anglais, valeurs en dur, code mort), avec `measure.py` ; la trace de génération par IA (typographie,
emoji, commentaires qui racontent, fichiers laissés) avec `scan.py` ; toute signature d'outil d'IA
dans les commits de la plage ; et les tests qui touchent les fichiers changés, un seul à la fois et à
basse priorité.

Chaque remarque donne le problème concret, le fichier et la ligne, et la correction. Une remarque par
problème, aucun compliment avant le sujet, aucun "pensez à extraire". Le verdict est Oui, Avec
corrections ou Non, et il ne peut pas être Oui tant qu'une remarque critique ou une signature d'IA
reste.

## Petit changement, PR déjà approuvée

Un petit changement a une relecture courte, jamais pas de relecture. "C'est trois lignes" ou "le
responsable a déjà validé" n'enlèvent aucun des contrôles. La relecture est faite avant toute
publication.

## Publier sur GitHub

Seulement si tu le demandes. Les remarques partent en commentaires simples, par la skill account-keys
quand elle est installée, avec le compte du propriétaire du dépôt, sinon avec tes propres identifiants
git. Une approbation ou une demande de changements part sous ton nom : elle ne
part que si tu l'as dit.

## Où vont les notes

Une relecture à garder est écrite dans `.ia/reviews/` du dépôt, exclu de git par `.git/info/exclude` et
jamais commité sauf demande. Le reste reste dans la conversation.

## Quand une autre skill l'appelle

Les remarques se traitent ensuite avec `receiving-code-review` (`/appliquer-relecture`). La relecture
est due après chaque tâche d'un plan lancé par `/executer`, et avant `/finir`. Un travail non commité
passe d'abord par clean-commits : la plage ne contient que des commits.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `reviewer-brief.md` est le texte donné au sous-agent
relecteur. Le dossier `scripts` contient `range.py`, qui trouve la base et la tête, liste les commits
et les fichiers changés et signale les signatures d'IA, et `scripts/lib` ce qu'il utilise. `tests`
contient les tests de ces scripts. `commands` contient la commande `/relecture`.
