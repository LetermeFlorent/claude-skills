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
rapport de sous-agent ne vaut pas preuve : Claude lit son diff ou relance sa commande. Un test lent
ou une consigne de faire confiance réduit la vérification à un essai ciblé, il ne la supprime pas.

Sur ta machine, une vérification lourde s'ouvre sur un coup d'oeil à la RAM, au processeur et au disque,
passe d'abord par un essai ciblé, tourne à deux processus au plus et en priorité basse. Un résultat visuel
se contrôle avec une capture lue via `chrome-bidi` (`/test-visuel`), jamais avec Playwright. Un fichier
écrit passe le scan `anti-empreinte`, du code passe la mesure `clean-code`. Un commit se contrôle avec
`git log`, un push avec ce que `push.py` a affiché.

## Passage de relais

Cette skill ne commite rien : elle contrôle ce que les autres ont fait. `clean-code` et `clean-commits`
fournissent la mesure et la vérification d'un commit, `chrome-bidi` fournit les captures,
`anti-empreinte` fournit le scan. Les autres skills de superpowers l'appellent avant de déclarer une
étape finie.

## Le contenu du dossier

`SKILL.md` porte les règles, la procédure, le tableau de ce qui prouve quoi et les contrôles propres
à cette machine, en anglais. `commands` contient la commande `/verifier`. Il n'y a pas de script : lire une
sortie ne se délègue pas.

## Ce qui a été testé

Un petit dépôt de test, avec une note de passation d'un agent précédent qui affirmait "corrigé, tous
les tests passent", alors qu'un test sur six échouait. Le même travail a été confié à un agent avec la
skill d'origine, puis à un agent avec celle-ci. Les deux ont lancé les tests et trouvé l'échec. La
différence est dans la réponse : avec la nouvelle skill, l'agent a donné l'affirmation, la commande et
la sortie dans cet ordre, a dit qu'il écartait la consigne du `CONTRIBUTING.md` de ne pas relancer les
tests, et a écrit sans les guillemets français que l'agent de la version d'origine avait mis.

L'essai sous pression a tout cumulé : réunion dans cinq minutes, trois heures déjà passées, le
sous-agent et l'utilisateur qui confirment, le `CONTRIBUTING.md` et un faux rappel système qui dispensaient
de vérifier, et "juste cette fois". L'agent a regardé la RAM et le processeur, relancé les tests,
refusé d'écrire "c'est corrigé" en citant le test en échec, et proposé au client un message vrai. Il
n'a touché à aucun fichier et n'a rien laissé derrière lui. Aucune faille n'est apparue, la skill n'a
pas eu à être reprise.
