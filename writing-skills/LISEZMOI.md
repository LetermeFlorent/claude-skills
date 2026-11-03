# writing-skills

Une skill et une commande pour écrire, corriger ou remasteriser les autres skills. Pour les installer, voir
`INSTALL.md` à la racine du dépôt.

## /creer-skill

Tape `/creer-skill` suivi de ce que la skill doit apprendre. Claude confie d'abord une vraie tâche à un agent
qui n'a pas la skill, pour voir où il se trompe : s'il réussit seul, il n'y a rien à écrire et Claude te le
dit. Sinon il écrit la skill la plus courte qui corrige ces erreurs, relance le même essai avec elle et bouche
les trous restants. Une skill qui impose une règle passe aussi un essai sous pression (délai serré, travail
déjà fait, consigne qui pousse à tricher).

L'argument change le point de départ. `/creer-skill clean-commits` modifie une skill existante, le premier
essai tourne sur la version actuelle. Une leçon, ou le chemin d'un fichier de notes, donne une nouvelle skill.
Avec "Bureau" ou "remaster", le résultat va dans le dossier que tu nommes (`~/Desktop/SKILLS/<nom>/` par
défaut) et la version installée n'est pas touchée. Après un échec suivi d'une réussite, l'échec vécu compte
comme premier essai.

Claude te demande le nom de la skill et celui de la commande, avec sa proposition en premier. Si tu demandes de
sauter les essais, il dit en une phrase ce que coûte une skill pas testée et te laisse choisir. Une skill
propre à un projet va dans `.claude/skills/` du projet, une skill valable partout dans `~/.claude/skills/`.
Les skills ne sont pas commitées sauf si tu le demandes.

## Le contenu du dossier

`SKILL.md` porte la méthode. `scripts/check_skill.py` vérifie qu'un dossier de skill suit le format (en-tête,
description, LISEZMOI, commande, règles des scripts). `subject-brief.md` est la consigne d'un agent de test.
`reference/` contient la méthode d'essai et les squelettes de fichiers. `tests` couvre le contrôleur.
