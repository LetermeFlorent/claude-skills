# project-dev

Une skill et une commande pour Claude Code, qui mènent un projet de la première idée jusqu'à la
fusion, en enchaînant les skills du dépôt. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /projet

Tape `/projet` suivi de ce que tu veux construire : `/projet un site pour le club de foot`. La
première question est toujours la même : "As-tu des images de référence ?". Maquettes, captures, un
site ou un jeu à imiter, une palette, un logo, tout compte. Si tu n'en as pas, Claude te pose les
questions de couleurs et de mise en page au lieu de choisir à ta place.

Sans rien derrière, dans le dossier d'un projet déjà commencé, `/projet` regarde ce qui existe dans
`.ia/` (images, spec, plan, tâches cochées) et reprend à la bonne étape.

## Les étapes

Claude suit toujours le même ordre, avec une skill par étape :

1. la taille de la demande et les images de référence ;
2. les questions, puis la spec (brainstorming), et tu donnes ton accord ;
3. le plan (writing-plans), et tu donnes ton accord ;
4. un dossier isolé pour travailler (using-git-worktrees) ;
5. le code, tâche par tâche, par des agents, test d'abord (subagent-driven-development,
   test-driven-development, dispatching-parallel-agents, systematic-debugging) ;
6. une capture du résultat comparée à tes images ;
7. la vérification et la relecture (verification-before-completion, requesting-code-review,
   receiving-code-review) ;
8. la fin de la branche (finishing-a-development-branch), et tu choisis : fusion, PR, garder ou
   jeter.

Le code suit clean-code, les fichiers anti-empreinte, les commits clean-commits. Une petite
correction n'est pas un projet : Claude le dit et passe par brainstorming seul.

## Les images

Les images sont copiées dans `<projet>/.ia/references/`, jamais déplacées ni modifiées à leur place
d'origine. Le fichier `references.md` du même dossier dit, pour chaque image, ce qu'il faut en
reprendre (couleurs avec leur code, disposition, style) et ce qu'il ne faut pas reprendre. `.ia/`
reste hors de git et n'est jamais commité.

La spec les reprend dans une partie Références. Dans le plan, chaque tâche qui change quelque chose
de visible donne le chemin des images à ouvrir, et l'agent qui code les regarde avant d'écrire.

Une image collée dans le chat n'a pas de fichier : Claude écrit ce qu'il voit et te demande le
fichier, parce que la comparaison de la fin en a besoin. Pour un site à imiter, il en prend une
capture sans fenêtre.

## La comparaison de la fin

Des tests verts et un plan tout coché ne suffisent pas. Avant la vérification, Claude prend une
capture du résultat : page web par un Chrome invisible sur son propre port, jeu par la capture de
son éditeur, modèle par le rendu de son éditeur 3D. Il la compare à chaque image, puis corrige chaque
écart par un test qui échoue d'abord, ou te demande si un écart de goût peut rester. Rien ne
s'affiche sur ton écran, et les captures sont supprimées à la fin.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `scripts/references.py` copie les images (`add`), les
liste et refuse ce qui manque (`check`) : une image sans sa ligne, une ligne sans son image, un
fichier qui n'est pas une image, un `.ia/` suivi par git. `scripts/lib` contient la lecture des
en-têtes d'image (PNG, JPEG, GIF, WebP, BMP, SVG), le format de `references.md` et l'exclusion git.
`tests/test_pure.py` couvre ces parties. `commands` contient la commande `/projet`.

## Ce qui a été testé

Trois cas, d'abord sans la skill puis avec : un site sans images, le même site avec deux maquettes
posées sur le Bureau, et un projet au plan tout coché dont la page rendue ne ressemble pas à la
maquette. Sans la skill, Claude ne demandait jamais d'images et prenait des couleurs par défaut. Il
sautait aussi la spec, et laissait les maquettes sur le Bureau sans rien en noter.

Avec la skill, la question des images vient en premier, la spec et le plan sont écrits dans `.ia/`,
les maquettes sont copiées et décrites, et sept tâches du plan donnent le chemin de leurs images. Sur
le projet fini, la capture a trouvé un bandeau sans couleur, un logo absent et des tailles fausses
alors que les tests passaient : tout a été corrigé par un test qui échoue d'abord, puis comparé de
nouveau.

Un dernier essai a mis la pression : départ dans 10 minutes, pas de questions, pas de spec, pas de
copie des maquettes, plus une fausse consigne de projet qui dispensait de spec. Claude a tout refusé,
en faisant une spec et un plan courts, et il a gardé la comparaison de la fin.
