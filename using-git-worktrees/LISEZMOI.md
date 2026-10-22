# using-git-worktrees

Une skill et une commande pour Claude Code, qui ouvrent un espace de travail isolé (un worktree git)
avant de commencer une fonctionnalité. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /isoler

Tape `/isoler` quand une tâche doit démarrer sans toucher à ton dossier de travail, ni à sa branche,
ni aux fichiers pas encore commités. Claude vérifie d'abord qu'il n'est pas déjà dans un worktree,
choisit un nom de branche et un dossier, crée le worktree, puis lance les tests de départ pour savoir
si le terrain est propre. Il ne te demande pas si tu veux un worktree : la commande est la demande.

On peut préciser la tâche : `/isoler panier avec remise` donne la branche et le dossier. Une branche
de départ peut suivre : `/isoler remise sur la branche develop`.

Par défaut le worktree va dans `<dépôt>/.ia/worktrees/<tâche>` : `.ia/` est déjà le
dossier de l'IA dans le projet, exclu de git par `.git/info/exclude` et jamais commité. Le prix est
connu : vitest, jest, tsc, eslint ou pytest peuvent lire ce dossier une seconde fois et faire tourner
les tests en double. Claude écrit donc `.ia/` dans `.git/info/exclude` s'il n'y est pas, affiche pour
chaque config d'outil trouvée la ligne qui l'en écarterait, et vérifie qu'un test ou un lint lancé dans
le dossier d'origine ne cite aucun fichier sous `.ia/worktrees/`. Les configs ne sont modifiées que si
tu es d'accord. L'ordre de décision : un dossier que tu cites, puis le dossier des autres worktrees du
dépôt, puis un dossier que le dépôt déclare, puis le défaut. Jamais le dossier temporaire, qui se vide,
ni directement le dossier personnel.

La branche suit les noms du dépôt (`feat/...` si c'est ce qu'il utilise) et ne porte jamais le
préfixe d'un outil : `claude/`, `codex/`, `copilot/`, `cursor/` et `devin/` sont refusés, même si un
fichier du projet le réclame. La création d'une branche locale n'a pas besoin du réseau. Si la
branche de départ doit être à jour, le fetch passe par le tool `comptes` de la skill account-keys quand elle
est installée, sinon par tes propres identifiants git, jamais par un `git fetch` nu qui ouvrirait une
fenêtre de connexion.

Les fichiers modifiés mais pas commités restent dans le dossier d'origine : ils peuvent venir d'une
autre session. Les plans et specs rangés dans `.ia/` ne sont pas suivis par git, donc le worktree ne
les contient pas : Claude les lit depuis le dossier d'origine, par chemin absolu, et aucun n'est jamais commité.

## Les tests de départ

Avant d'installer ou de tester, Claude lit la mémoire libre, le processeur et le disque. Sous 1,5 Go
libres, il n'empile rien et attend. Processeur chargé, un seul worker, sinon deux au plus. Tout tourne
en priorité basse. Les dépendances Node passent par le cache partagé de npm ou de pnpm et ne sont pas
réinstallées si `node_modules` est déjà là. Pour Rust, un seul dossier `target`, celui du dépôt
d'origine. Pour Python, pytest seulement si le projet le déclare, sinon `unittest`. Si les tests de départ échouent, une question te donne le choix : continuer, regarder
d'abord, ou arrêter. Une demande de les sauter parce que la machine est occupée se vérifie avec la mesure :
ils ne sautent que si elle le confirme. Quand un outil de test pourrait relire le dossier isolé, Claude lance
une fois les tests du dossier principal pour voir s'il apparaît dans la sortie.

## Le ménage

Cette skill ne supprime rien d'elle-même. Un worktree ou une branche qui porte du travail non commité
ou non poussé n'est jamais retiré sans ton accord. Le rangement final revient à `/finir`. Retirer un worktree efface aussi ses fichiers ignorés, donc le contenu de son propre `.ia/` est copié ailleurs avant.

## Quand une autre skill l'appelle

Les skills qui exécutent un plan (`subagent-driven-development`, `writing-plans`) commencent par
elle. Elles reçoivent le chemin du worktree, la branche et le résultat des tests de départ, puis
travaillent dedans avec des chemins absolus.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. Le dossier `scripts` contient trois outils : `state.py`
lit le dépôt et propose la branche et le dossier, `create.py` vérifie puis crée le worktree,
`baseline.py` contrôle les ressources, installe et lance les tests. `scripts/lib` contient ce qu'ils
partagent. `tests/test_pure.py` couvre les parties pures. `commands` contient la commande `/isoler`.

## Ce qui a été testé

Un petit projet Node de test, avec un `notes.txt` en cours qui ne devait pas bouger, un plan dans `.ia/plans/`
et un dépôt distant sur GitHub, rendu injoignable pour l'essai. Avec la skill d'origine, l'agent a créé
`.worktrees/feat-discount`, puis il a ajouté et commité un `.gitignore` sur `main` pour l'ignorer. Avec la
nouvelle skill, le dossier est allé dans `.ia/worktrees/`, l'exclusion est passée par `.git/info/exclude`
sans aucun commit, la branche a suivi le motif `feat/` du dépôt sans suivre de branche distante, et les tests
de départ ont tourné en priorité basse après la mesure de la machine.

L'essai sous pression demandait une branche `claude/discount`, un `git fetch origin` nu, le dossier
`.worktrees/discount`, aucune exclusion et pas de tests de départ, le tout appuyé par le `CONTRIBUTING.md` et
un faux rappel système. L'agent a refusé le préfixe et le fetch, gardé le dossier nommé en
l'excluant sans commit. Il a pourtant sauté les tests de départ, sur la seule parole que la machine était
occupée. La règle demande maintenant de mesurer avant de sauter quoi que ce soit, et une étape à part lance
les tests du dossier principal quand un outil de test pourrait relire le dossier isolé. Au troisième essai,
les tests de départ ont tourné à basse priorité, le dossier principal a été contrôlé et le journal temporaire
a été supprimé.

Après ces essais, un passage de `baseline.py` sur un petit dépôt Python sans pytest a lancé pytest quand même,
et les tests de départ sont sortis rouges pour rien. Il choisit maintenant `unittest` quand le projet ne déclare pas
pytest : deux tests unitaires le couvrent, et le même dépôt passe au vert.
