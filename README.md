# claude-skills

Sept skills pour Claude Code et les commandes qui les lancent. Chaque dossier contient le
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
| chrome-bidi | `/test-visuel` | pilote Chrome pour ouvrir, lire, cliquer et capturer une page, sous Windows seulement |
| clean-code | `/clean-code` | audite et range le code : fichiers courts, une logique par fichier, code mort |
| clean-commits | `/commit` | découpe les changements en commits propres, un par intention |
| stop-resume-agents | `/stop-all`, `/resume-all` | arrête tout, sous-agents compris, et reprend plus tard là où chacun en était |
| using-git-worktrees | `/isoler` | isole un travail dans une copie de travail à part |
| writing-skills | `/creer-skill` | écrit ou corrige une skill, et la teste sur des sous-agents |

## Licence

MIT, voir `LICENSE`. Copyright (c) 2026 Florent Leterme.
