# using-git-worktrees

Une skill et une commande pour ouvrir un espace de travail isolé (un worktree git) avant de commencer une
fonctionnalité. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /isoler

Tape `/isoler` quand une tâche doit démarrer sans toucher à ton dossier, à sa branche ni aux fichiers pas
encore commités. Claude vérifie qu'il n'est pas déjà dans un worktree, choisit une branche et un dossier,
crée le worktree, puis lance les tests de départ. Il ne demande pas si tu veux un worktree : la commande
est la demande. Un argument donne la tâche (`/isoler panier avec remise`) et, au besoin, la branche de
départ (`/isoler remise sur la branche develop`).

Le worktree va par défaut dans `<dépôt>/.ia/worktrees/<tâche>`, un dossier exclu de git sans toucher à
`.gitignore`. Un dossier que tu cites, ou que le dépôt déclare, passe avant. Jamais le dossier temporaire ni
le dossier personnel. Vitest, jest, tsc, eslint ou pytest peuvent lire ce dossier une seconde fois : Claude
affiche la ligne de config qui l'en écarterait et ne la modifie que si tu es d'accord.

La branche suit les noms du dépôt et ne porte jamais un préfixe d'outil (`claude/`, `codex/`, `copilot/`,
`cursor/`, `devin/`). Aucun `git fetch` nu : il ouvrirait une fenêtre de connexion. Les fichiers modifiés mais
pas commités restent dans ton dossier d'origine.

## Les tests de départ

Claude mesure d'abord la mémoire, le processeur et le disque. Sous 1,5 Go libres il attend, sinon il lance
l'installation et les tests en priorité basse, avec deux workers au plus. Si les tests échouent, il te laisse
choisir : continuer, regarder d'abord, ou arrêter.

## Retirer un worktree

Seulement sur ta demande. Un worktree ou une branche qui porte du travail non commité ou non poussé n'est
jamais retiré sans ton accord.

## Le contenu du dossier

`SKILL.md` porte la procédure. `scripts` contient `state.py` (lit le dépôt, propose branche et dossier),
`create.py` (vérifie puis crée) et `baseline.py` (ressources, installation, tests), avec leurs morceaux
communs dans `scripts/lib`. `tests/test_pure.py` couvre les parties pures.
