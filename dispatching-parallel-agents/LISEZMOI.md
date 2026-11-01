# dispatching-parallel-agents

Une skill et une commande pour Claude Code, qui répartissent du travail entre plusieurs sous-agents
lancés en même temps. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /paralleliser

Tape `/paralleliser` quand plusieurs tâches n'ont pas besoin les unes des autres : trois fichiers de
tests qui échouent pour des raisons différentes, quarante fichiers à lire pour une seule question,
la même modification sur trente fichiers. Claude découpe le travail par domaine, écrit pour chaque
agent un message précis (les fichiers exacts, ce qu'il a le droit de modifier, ce qu'il doit
rendre), puis les envoie tous dans le même message pour qu'ils tournent ensemble.

On peut préciser : `/paralleliser les trois fichiers de tests en rouge` donne la liste du travail à
répartir. Sans précision, Claude part de ce qui est en cours dans la conversation et propose un
découpage.

Avant l'envoi, un test d'indépendance : deux agents ne modifient jamais le même fichier, ne partagent
ni un port de serveur, ni un port de débogage Chrome, ni une instance de Roblox Studio, de Blender
ou d'Audacity (une instance par agent, toujours nommée). Le script `scripts/overlap.py` fait cette
vérification sur un plan écrit en JSON. Deux tâches qui touchent le même fichier passent l'une après
l'autre.

Les agents sont en sonnet par défaut, en opus seulement quand la tâche le demande, et Claude ne
change jamais l'effort sans que tu le demandes. Aucun agent ne reconstruit une image docker ou next,
ne recrée un conteneur, ne fait de commit : la session principale reconstruit une fois avant, et
commite à la fin, par clean-commits. Avant d'envoyer des agents qui lancent des commandes lourdes,
Claude regarde une fois la mémoire, le processeur et le disque, et ne laisse pas tourner plus de deux
processus lourds à la fois, à priorité basse.

Claude ne garde que la conclusion de chaque agent, relance lui-même la vérification complète, arrête
et supprime tout agent qui s'égare, et vérifie la liste des agents avant de finir.

## Arrêter et reprendre

Pour tout figer, agents compris, et retrouver plus tard où chacun en était, la skill
`stop-resume-agents` : `/stop-all` puis `/resume-all`.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `agent-brief.md` est le modèle du message donné à chaque
agent. `scripts/overlap.py` contrôle un plan de répartition, `scripts/lib` lit le plan et applique les
règles, `tests` contient le test unitaire, `commands` la commande `/paralleliser`.
