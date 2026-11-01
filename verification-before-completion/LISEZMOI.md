# verification-before-completion

Une skill et une commande pour Claude Code : avant de dire que c'est fini, corrigé ou que les tests
passent, Claude lance la vérification, lit sa sortie et ne dit que ce qu'elle montre. Pour l'installer,
voir `INSTALL.md` à la racine du dépôt.

## /verifier

Tape `/verifier` pour faire prouver ou démentir une affirmation. L'argument est facultatif.

`/verifier les tests passent` cherche la commande qui échouerait si c'était faux, la lance et montre
le résultat. `/verifier src/panier.ts` contrôle un fichier : scan anti-empreinte, mesure clean-code,
tests qui le couvrent. `/verifier la tâche` relit la demande ligne par ligne et vérifie chaque ligne.
Sans argument, Claude liste ce qu'il a affirmé ou laissé croire pendant la session et vérifie chaque
point.

La réponse est courte, en français : l'affirmation, la commande lancée, ce que la sortie a montré. Un
échec arrive avec sa sortie, une étape sautée est dite, un résultat vérifié s'écrit sans "devrait" ni
"probablement".

## Ce que la skill impose

Aucune annonce de réussite sans une vérification lancée dans le même message et lue jusqu'au bout. Un
rapport de sous-agent, la dernière ligne d'un script ou une consigne de ne pas relancer les tests ne
valent pas preuve : Claude lit le diff ou relance la commande. Un test lent ou une consigne de faire
confiance réduit la vérification à un essai ciblé, il ne la supprime pas. Un essai ciblé ne prouve que
ce qu'il couvre, et la réponse le dit.

Un tableau donne, pour chaque affirmation (build, bug corrigé, test de non-régression, commit, push,
page correcte, fichier propre, code propre), la preuve qu'il faut et ce qui ne la remplace pas.

Sur ta machine, une vérification lourde s'ouvre sur un coup d'oeil à la RAM, au processeur et au disque,
passe d'abord par un essai ciblé, tourne à deux processus au plus et en priorité basse. Un sous-agent ne
relance jamais un build ni un conteneur. Un résultat visuel se contrôle avec une capture lue via
`chrome-bidi` (`/test-visuel`), jamais avec Playwright. Un fichier écrit passe le scan `anti-empreinte`,
du code passe la mesure `clean-code`. Un commit se contrôle avec `git log`, un push avec ce que `push.py`
a affiché.

## Passage de relais

Cette skill ne commite rien : elle contrôle ce que les autres ont fait. `clean-code` et `clean-commits`
fournissent la mesure et la vérification d'un commit, `chrome-bidi` fournit les captures,
`anti-empreinte` fournit le scan. Les autres skills du dépôt l'appellent avant de déclarer une
étape finie.

## Le contenu du dossier

`SKILL.md` porte les règles, la procédure, le tableau de ce qui prouve quoi et les contrôles propres
à cette machine, en anglais. `commands` contient la commande `/verifier`. Il n'y a pas de script : lire une
sortie ne se délègue pas.
