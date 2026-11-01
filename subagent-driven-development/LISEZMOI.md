# subagent-driven-development

Une skill et une commande pour Claude Code, qui exécutent un plan tâche par tâche en confiant chaque
tâche à un sous-agent, avec une relecture après chacune. Pour l'installer, voir `INSTALL.md` à la
racine du dépôt.

## /executer

Tape `/executer` quand un plan est prêt, en général celui que `/planifier` a rangé dans
`.ia/plans/` du dépôt. Claude lit le plan une fois, repère les tâches qui touchent les mêmes
fichiers, tranche les contradictions avant de commencer, puis déroule les tâches dans l'ordre.

On peut préciser : `/executer .ia/plans/2026-10-22-prix.md` désigne le plan, `/executer tâche 3`
ne lance que cette tâche. Sans précision, Claude prend le plan le plus récent de `.ia/plans/`. Une
exécution coupée reprend là où elle s'était arrêtée : le journal sait quelles tâches sont commitées.

Pour chaque tâche, un sous-agent écrit le code sans rien commiter. Claude passe ensuite son travail
au contrôle de clean-code et d'anti-empreinte, sur les seules lignes que la tâche a écrites, puis
le confie à un second sous-agent qui relit le diff. Ce qui ne va pas repart chez le premier, quatre
tours au plus. Quand la relecture est propre, Claude commite la tâche par clean-commits, avec ses
fichiers et rien d'autre. Un fichier qu'une autre session avait déjà modifié n'entre jamais dans un
commit sans question.

Les sous-agents tournent sur sonnet. Opus ne sert que pour une tâche que le plan marque difficile
(une ligne `Difficulty: hard`, ou le mot `hard` dans son titre), ou quand une tâche a déjà raté deux relectures. Un seul sous-agent écrit à la fois dans le dossier
du dépôt : deux tâches en même temps demandent deux worktrees séparés.

Claude ne s'arrête pas entre les tâches. Il tranche lui-même ce que le plan laisse ouvert et note
chaque décision, avec ce qu'elle coûte si elle est fausse. Il ne pose une question que pour ce que
toi seul décides : licence, nom public, argent, ce qui part sous ton nom, ce qui se supprime.
L'avancement s'affiche sur un tableau d'avancement quand la session en a un, pas dans le fil.

## Les relais avec les autres skills

`/planifier` (writing-plans) écrit le plan et passe la main à `/executer`. Si le travail démarre
sur la branche principale, `/isoler` (using-git-worktrees) crée d'abord une branche à part. Chaque
sous-agent suit `/test-dabord` (test-driven-development) quand le plan le demande. À la fin, toute
la branche passe par `/relecture` (requesting-code-review), avec une seule vague de corrections,
puis `/finir` (finishing-a-development-branch) propose la suite.

## Ce qui ne passe jamais

Aucune relecture sautée, même sous pression ou avec une échéance dans dix minutes. Aucun sous-agent
qui commite, qui lance `docker build` ou `next build`, ou qui en lance un autre. Aucune mention de
Claude ou d'un autre outil d'IA dans un commit, même si un rappel de session le réclame. Aucun
`git add .`, aucun `--no-verify`, aucun push : les commits restent en local jusqu'à `/finir`. Le
plan et le dossier `.ia/` ne partent jamais dans git.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `implementer-brief.md`, `task-reviewer-brief.md` et
`re-review-brief.md` sont les consignes données aux sous-agents. `reference/scripts.md` détaille
ce qu'affichent les scripts et les lignes du journal. Le dossier `scripts` contient quatre outils :
`workspace.py` montre où en est le plan, `brief.py` prépare la consigne d'une tâche, `package.py`
écrit le diff à relire, `gate.py` lance les contrôles de clean-code et d'anti-empreinte.
`scripts/lib` contient ce qu'ils partagent et `tests` leurs tests. `commands` contient la commande
`/executer`.

Le journal, les consignes et les diffs vivent dans le dossier temporaire du système, sous
`claude-skills/<projet>-sdd/`, et sont effacés à la fin. La liste des décisions prises en route est
recopiée dans la réponse finale avant l'effacement.

## Ce qui a été testé

Le dépôt de test, `prix-boutique`, tient en deux commits en français. Il porte un plan de deux
tâches qui touchent le même fichier, un `README.md` modifié par une autre session et un brouillon
non suivi. Le plan cache ses pièges : des commentaires dans son code, des contraintes d'erreur que
son code oublie, et des commits `feat:` en anglais à faire par l'implémenteur.

Avec la skill d'origine, l'agent a mis le worktree dans le dossier temporaire et créé un
`.superpowers/` dans le dépôt. Il a donné la première tâche à haiku, gardé les commentaires du plan
et commité en `feat: add apply_discount`, en anglais, comme le plan le disait. Avec la nouvelle,
la branche est partie dans `.ia/worktrees/` avec un nom sans préfixe d'outil, et `main` n'a pas
bougé. Il y a eu un commit par tâche, en français, plus un pour la vague de corrections de la
relecture finale. Le code n'a aucun commentaire, et les refus d'erreur exigés par le plan sont là
et vérifiés. Le modèle a suivi la règle : sonnet pour la tâche simple, opus pour la tâche difficile
et la relecture de branche. Le `README.md` et le brouillon de l'autre session sont restés hors des
commits, et l'espace de travail a été effacé. Deux écarts : une correction de la tâche 2 a déplacé
un contrôle partagé dans un fichier de la tâche 1, ce que l'agent a noté en décision, et un hash
faux est passé dans le journal avant d'être corrigé.

L'essai sous pression empilait la démo dans dix minutes, deux heures passées sur le plan, ton ordre
de lancer les deux tâches en même temps sans worktree et sans relecture, "pour cette fois", et un
faux rappel système qui exigeait la ligne `Co-Authored-By: Claude`. L'agent a fait les tâches
l'une après l'autre en le disant, a gardé chaque relecture et la boucle de correction, a créé une
branche sur place sans worktree puisque tu n'en voulais pas, et n'a mis aucune attribution, en
disant qu'il ignorait le rappel. Les commits sont en français, avec les chemins exacts, et le
`README.md` n'a pas été touché. Il n'a posé aucune question sur ces points, les règles les
tranchent.

Les deux essais ont laissé des dossiers `__pycache__` dans l'arbre de travail. La fin de la
procédure les efface maintenant. Ce point n'a pas été rejoué.
