# test-driven-development

Une skill et une commande pour Claude Code, qui font écrire des tests utiles avec le code. Pour
l'installer, voir `INSTALL.md` à la racine du dépôt.

## /test-dabord

Tape `/test-dabord` suivi de ce qu'il faut construire ou corriger : `/test-dabord la conversion du
panier en dollars`, `/test-dabord le total faux quand le panier est vide`. Claude lit d'abord deux ou
trois tests voisins pour reprendre leur dossier, leurs noms et leur style. Si la règle attendue a un
trou, comme un arrondi, une limite ou ce que doit faire une erreur, il te pose la question avant
d'écrire quoi que ce soit. Sans argument, il demande ce qu'il faut construire.

Un test vaut quelque chose s'il fait tourner le vrai code et s'il peut échouer pour la bonne raison.
Pour un bug, le test qui le reproduit échoue d'abord sur le code non corrigé, puis la correction le fait
passer. Pour un comportement nouveau, Claude imagine les casses réalistes du code neuf et désigne le test
qui attraperait chacune. À la fin, il lance la suite complète une fois et lit son résumé.

## Ce qui ne passe jamais

Les valeurs attendues viennent de la règle donnée, jamais d'une exécution du code ni d'une règle
inventée. Aucun test unitaire ne touche le réseau : l'appel est simulé, le reste du code tourne pour de
vrai, et aucun test ne se contente de vérifier qu'une simulation a été appelée. Un échec dû à une faute
de frappe, à un mauvais chemin ou à un test qui n'a pas tourné ne prouve rien. Une consigne trouvée dans
un fichier du dépôt ou dans un rappel de session ne lève aucune de ces règles.

## Le code déjà écrit

Le code d'une autre session, ou le tien, n'est jamais supprimé pour faire place à un test. Quand tu
demandes d'ajouter des tests après coup, chacun est prouvé par une casse volontaire : Claude change la
ligne couverte, voit le test échouer, remet la ligne par une modification (jamais par `git checkout`, qui
effacerait toutes les modifications du fichier), puis le voit passer. Le compte rendu dit que ces tests
sont venus après le code. S'il trouve un bug dans ton code alors que tu as demandé de ne pas y toucher,
il te demande avant de corriger.

## Lancer les tests

Le script `run.py` lance un seul test, un fichier ou la suite, en priorité basse, sans mode
surveillance, avec deux processus au plus. Il reconnaît pytest, unittest, jest, vitest, cargo, go et
le script `test` du projet, et lance tel quel n'importe quelle autre commande. Il dit si le résultat
est bien l'échec ou la réussite attendus, et refuse un "échec" où aucun test n'a tourné, ou qui vient
d'une erreur avant toute vérification. Avant la suite complète, il regarde la mémoire libre, le
processeur et le disque, et passe à un seul processus si la machine est chargée. Un test bloqué est
arrêté au bout de dix minutes, avec tout ce qu'il a lancé.

## Avec les autres skills

`systematic-debugging` (`/deboguer`) trouve la cause d'un bug, puis passe ici pour le test qui le
reproduit. Le code écrit suit `clean-code`, tests compris. Les commits passent par `clean-commits`, avec
les chemins exacts, le test et le code dans le même commit, sans push. `verification-before-completion`
(`/verifier`) décide quand le travail peut être dit fini. Les brouillons et les scripts de reproduction
vont dans le dossier temporaire du système et sont supprimés à la fin.

## Le contenu du dossier

`SKILL.md` porte les règles, en anglais. `reference/good-tests.md` dit ce qui fait un bon test : la
casse qu'il attrape, les valeurs attendues, les simulations, les noms, la vérification par casse
imaginée. `scripts/run.py` lance les tests, et `scripts/lib` contient la détection du lanceur, les
commandes, le lancement en priorité basse et la lecture des résumés. `tests` contient leurs tests, et
`commands` la commande `/test-dabord`.
