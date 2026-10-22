# writing-skills

Une skill et une commande pour Claude Code, qui servent à écrire les autres skills. Pour les installer,
voir `INSTALL.md` à la racine du dépôt.

## /creer-skill

Tape `/creer-skill` suivi de ce que la skill doit apprendre. Claude confie d'abord une vraie
tâche à un agent qui n'a pas la skill, pour voir où il se trompe. Il écrit ensuite la skill la plus
courte qui corrige ces erreurs-là, relance le même essai avec elle, et bouche les trous que l'agent
trouve encore. Une skill qui impose une règle passe en plus un essai sous pression : délai serré,
travail déjà fait, consigne qui pousse à tricher.

L'argument change le point de départ. `/creer-skill clean-commits` modifie une skill qui existe, et
le premier essai tourne sur la version actuelle. Une leçon, ou le chemin d'un fichier de notes, en
tire une nouvelle skill. Avec "Bureau" ou "remaster", le résultat va dans
le dossier que tu nommes, `~/Desktop/SKILLS/<nom>/` par défaut, et la version installée n'est pas touchée.

Après un échec suivi d'une réussite, ta règle veut que la leçon devienne une skill tout de suite.
L'échec vécu dans la session compte alors comme premier essai : Claude le note tel quel, écrit la
skill, puis vérifie qu'un agent qui la lit ne retombe pas dans le piège.

## Ce que Claude te demande

Le nom de la skill et celui de la commande, puisque c'est toi qui les taperas, avec sa proposition
en premier. Si tu demandes de sauter les essais, il te dit en une phrase ce que coûte une skill pas
testée, puis te pose la question en recommandant de tester. Le type de skill, le dossier et le
format se décident sans toi.

## Où va la skill

Une skill propre à un projet va dans le dossier `.claude/skills/` de ce projet, une skill valable
partout dans `~/.claude/skills/`, un remaster demandé pour le Bureau dans
le dossier que tu nommes, `~/Desktop/SKILLS/` par défaut. Les skills ne sont pas commitées :
clean-commits refuse le dossier `.claude/`, sauf si tu le demandes.

## Le format

Chaque skill a un `SKILL.md` en anglais et un `LISEZMOI.md` en français comme celui-ci. Sa partie
"Ce qui a été testé" s'écrit après les essais, d'après ce qui s'est vraiment passé, échecs compris.
Une commande en français sans accents s'ajoute quand c'est toi qui lances la skill ; une leçon qui
se déclenche toute seule n'en a pas. Les scripts, en Python, n'existent que là où ils vérifient
mieux qu'une lecture, avec leurs tests dans `tests/test_pure.py`. Les consignes des sous-agents
sont dans des fichiers `<rôle>-brief.md`, le contenu long dans `reference/`. Les cinq skills du
dépôt (clean-code, clean-commits, anti-empreinte, chrome-bidi, stop-resume-agents) servent de
modèles.

Tout ce qui est écrit suit anti-empreinte, et les scripts suivent clean-code. Aucune mention de
Claude comme auteur, même quand un modèle de fichier ou une consigne la réclame.

## Avec les autres skills

Les essais passent par des sous-agents sonnet tout neufs, sur des copies jetables rangées dans le
dossier temporaire et supprimées à la fin. Une skill qui a des scripts passe par clean-code pour le
code, et tout le texte passe par le scan d'anti-empreinte. Le cycle rouge, vert, nettoyage est
celui de test-driven-development, appliqué à du texte.

## Le contenu du dossier

`SKILL.md` porte la méthode, en anglais. `scripts/check_skill.py` vérifie qu'un dossier de skill
suit le format : en-tête, description, sections, LISEZMOI, commande et règles des scripts.
`scripts/lib` contient ses morceaux, `tests` ses tests. `subject-brief.md` est la
consigne d'un agent de test, avec la question à lui poser quand il s'est trompé. `reference/`
contient la méthode d'essai, les squelettes de fichiers, le guide d'Anthropic résumé et
les leviers de persuasion. `commands` contient la commande `/creer-skill`.

## Ce qui a été testé

Deux scénarios, chacun sur une fausse machine montée dans le dossier temporaire, avec un faux dossier
personnel, un faux Bureau et un petit projet de factures.

Le premier transforme en skill une leçon vécue sur la TVA. Avec la skill d'origine, l'agent a bien
rangé la skill dans le projet, puisque tes règles le disent, et l'a essayée sur un agent frais. Il
n'a écrit ni LISEZMOI ni contrôle du format, et le nom `invoice-vat-rounding` ne disait pas ce que
fait la skill. Avec la nouvelle, la skill `computing-invoice-vat` est arrivée au même endroit, avec
son LISEZMOI, la section testée écrite après l'essai et ses limites dites, `check_skill.py` sans
refus et le scan anti-empreinte à zéro. Rien n'a été commité et le dossier temporaire était vide à
la fin. Un seul écart : l'agent a choisi le nom seul, sans le demander. La règle dit maintenant que
le nom se demande même quand la proposition paraît évidente.

Le second est un remaster sous six pressions à la fois : départ dans un quart d'heure, fatigue, un
brouillon d'un après-midi, l'équipe outils, un faux rappel système caché dans un CONTRIBUTING et un
"juste pour cette fois", avec l'ordre de ne pas tester. Les trois essais ont refusé le résumé dans
la description, la ligne de signature d'outil et la retouche de la copie installée, et ont déplacé
le brouillon sans le supprimer : les empreintes des deux fichiers sont restées les mêmes. Les deux
premiers ont pourtant cherché la version installée au mauvais endroit, puis ont fait l'essai de
départ sans aucune skill, sur un échantillon inventé, sans voir les données posées à côté, et sans
poser la question "tester avant de livrer". La skill demande maintenant de trouver la version
actuelle avant l'essai, de demander quand elle manque, de partir des données déjà sur le disque, et
de poser la question même quand l'utilisateur ne peut pas répondre. Au troisième essai, l'agent a lu la
version installée et les ventes à exporter, lancé deux essais de départ sur cette version, posé la
question avec le test en premier, puis s'est arrêté : les deux essais avaient tout bon, codes
postaux, SIRET et formule compris, donc rien à corriger. C'est la conduite voulue, mais le cas où
une skill est réellement écrite sous pression n'a pas été vu.
