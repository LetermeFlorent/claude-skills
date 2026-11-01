# claude-skills

Dix-huit skills pour Claude Code et les commandes qui les lancent. Chaque dossier contient le
`SKILL.md` que lit l'IA, un `LISEZMOI.md` en français pour toi, et ses scripts et ses tests quand
elle en a.

## Installer

Demande à ton IA de suivre `INSTALL.md`. Elle copie le dépôt dans le dossier de configuration de
Claude Code, relie les skills et copie les commandes, sans rien écraser de ce qui porte déjà le même
nom chez toi.

Ensuite, chaque skill regarde une fois par session s'il existe une version plus récente sur GitHub.
Si oui, l'IA la récupère, relit la skill et continue. Une copie que tu as modifiée n'est jamais
touchée.

## Les skills

Chaque ligne donne la commande qui lance la skill et ce qu'elle fait.

| Skill | Commande | Rôle |
|---|---|---|
| anti-empreinte | `/anti-empreinte` | écrit et corrige textes et code sans les marques d'un texte d'IA |
| brainstorming | `/concevoir` | pose les questions avant la moindre ligne, puis écrit la conception |
| chrome-bidi | `/test-visuel` | pilote Chrome pour ouvrir, lire, cliquer et capturer une page, sous Windows seulement |
| clean-code | `/clean-code` | audite et range le code : fichiers courts, une logique par fichier, code mort |
| clean-commits | `/commit` | découpe les changements en commits propres, un par intention |
| dispatching-parallel-agents | `/paralleliser` | répartit des tâches indépendantes entre plusieurs sous-agents |
| finishing-a-development-branch | `/finir` | termine une branche : fusion, pull request, garder ou jeter |
| project-dev | `/projet` | mène un projet neuf de bout en bout, images de référence comprises |
| receiving-code-review | `/appliquer-relecture` | trie les retours d'une relecture avant d'en appliquer un seul |
| requesting-code-review | `/relecture` | fait relire un changement avant de passer à la suite |
| stop-resume-agents | `/stop-all`, `/resume-all` | arrête tout, sous-agents compris, et reprend plus tard là où chacun en était |
| subagent-driven-development | `/executer` | exécute un plan tâche par tâche avec des sous-agents |
| systematic-debugging | `/deboguer` | cherche la cause d'un bug avant de proposer une correction |
| test-driven-development | `/test-dabord` | écrit le test avant le code, un test qui peut vraiment échouer |
| using-git-worktrees | `/isoler` | isole un travail dans une copie de travail à part |
| verification-before-completion | `/verifier` | lance la vérification avant d'annoncer que c'est fini |
| writing-plans | `/planifier` | découpe une conception en tâches courtes, chacune avec son test |
| writing-skills | `/creer-skill` | écrit ou corrige une skill, et la teste sur des sous-agents |

## Licence

MIT, voir `LICENSE`. Copyright (c) 2026 Florent Leterme.
