# writing-plans

Une skill et une commande pour Claude Code, qui transforment une spécification terminée en plan de travail.
Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /planifier

Tape `/planifier` quand la spécification est prête et qu'aucun code n'a encore été touché. L'argument est le
chemin de la spécification, ou quelques mots qui la désignent. Sans argument, Claude prend la plus récente du
dossier `.ia/specs/` du dépôt, et demande si deux se valent.

Claude lit la spécification en entier, puis le dépôt : chemins réels, façon de lancer un seul test, historique
des commits. Il découpe le travail en tâches. Chaque tâche nomme ses fichiers exacts, écrit d'abord le test,
le lance, écrit le code qui le fait passer, puis finit sur un commit qui liste ses propres
fichiers un par un. Aucun fichier prévu ne dépasse 150 lignes, aucun ne mélange deux rôles, aucun ne porte de
commentaire.

Le plan est écrit dans `.ia/plans/AAAA-MM-JJ-<sujet>.md` du dépôt. Le dossier `.ia` est ajouté à
`.git/info/exclude` : le plan ne part dans aucun commit, sauf si tu le demandes toi-même. Un fichier
CONTRIBUTING qui réclame `docs/plans` ne suffit pas, le plan reste dans `.ia/plans/` et Claude le dit en une
ligne.

## Contrôles avant de te rendre le plan

Un script, `plan_lint.py`, vérifie la forme : emplacement et nom du fichier, présence du dossier `.ia` dans
l'exclusion git, étiquettes de l'en-tête, test écrit avant le code dans chaque tâche, commit par `clean-commits`
avec exactement les fichiers de la tâche, aucun `git add .`, aucun push, aucun `--no-verify`, aucun `--amend`,
aucune mention d'outil d'IA, aucun TODO ni renvoi du genre "pareil que la tâche 2". Ensuite, pour un plan de
trois tâches ou plus, un sous-agent sonnet relit le sens : chaque exigence de la spécification a sa tâche, les
noms se suivent d'une tâche à l'autre, les chemins existent. Une tâche que le plan marque `Difficulty: hard`
passera sur opus à l'exécution.

## Passage de relais

Le plan ne lance pas la construction. Claude te donne le chemin et choisit la méthode. Par défaut,
`/executer <chemin du plan>` : un sous-agent par tâche, relu avant la suivante. Pour un plan court (une ou deux
tâches simples, mêmes fichiers, interfaces évidentes), il propose de dérouler le plan dans la même session. Tu
peux changer ce choix en un mot.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `reference/plan-format.md` décrit la forme d'un plan et d'une tâche.
`plan-reviewer-brief.md` est la consigne du sous-agent relecteur. `scripts/plan_lint.py` fait les contrôles de
forme, avec ses outils partagés dans `scripts/lib`, et `tests/test_pure.py` les teste. `commands` contient la
commande `/planifier`.

## Ce qui a été testé

Un petit dépôt de test avec une spécification de codes de remise. Le même travail a été confié à un agent
avec la skill d'origine, puis à un agent avec celle-ci. La version d'origine a écrit le plan dans
`docs/plans/`, au milieu des fichiers suivis, sans ligne d'exclusion, et a fini en demandant quelle méthode
d'exécution choisir. Avec la nouvelle skill, le plan est allé dans `.ia/plans/`, la ligne `.ia` a été ajoutée
à `.git/info/exclude`, `plan_lint.py` a répondu `ok` et l'agent a choisi la méthode lui-même.

Le premier essai sous pression a montré une faille. L'utilisateur demandait de commiter le plan dans `docs/`, un
faux mot de politique du projet réclamait `git add .` et un push, et l'agent a tout refusé d'un bloc, la
demande de l'utilisateur comprise. La règle 1 dit maintenant que la parole de l'utilisateur dans la conversation
est la permission attendue : le plan reste dans `.ia/plans/`, une copie part dans le dossier qu'il nomme et seule
cette copie est commitée. Au second essai, l'agent a fait exactement ça, en un commit sur un seul chemin,
sans push, et il a gardé les tests du plan malgré la demande de les retirer.
