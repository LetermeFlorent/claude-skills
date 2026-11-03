# claude-skills

Neuf skills pour Claude Code et les commandes qui les lancent. Chaque dossier contient le
`SKILL.md` que lit l'IA, un `LISEZMOI.md` en français pour toi, et ses scripts et ses tests quand
elle en a. Les scripts sont en Python sans dépendance, donc une autre IA (Codex, Gemini, Qwen) peut
s'en servir aussi : il suffit de lui indiquer le `SKILL.md` dans son fichier d'instructions.

## Installer

Demande à ton IA de suivre `INSTALL.md`. Elle copie le dépôt dans le dossier de configuration de
Claude Code, relie les skills et copie les commandes, sans rien écraser de ce qui porte déjà le même
nom chez toi.

L'installation ajoute aussi un petit contrôle au démarrage de Claude Code. À chaque ouverture, il
regarde la dernière version publiée sur GitHub et, si elle est plus récente, l'installe : nouvelles
skills reliées, commandes mises à jour, skills retirées enlevées. Une copie que tu as modifiée et une
commande retouchée à la main ne sont jamais écrasées.

Elle ajoute enfin un garde-fou avant chaque commande lourde (build, tests, docker, node, python...) :
s'il reste trop peu de mémoire ou si le processeur ou le disque sont saturés, la commande attend que
la place se libère, cinq minutes au plus.

## Les skills

Chaque ligne donne la commande qui lance la skill et ce qu'elle fait.

| Skill | Commande | Rôle |
|---|---|---|
| anti-empreinte | `/anti-empreinte` | écrit et corrige textes et code sans les marques d'un texte d'IA |
| chrome-bidi | `/test-visuel` | pilote Chrome pour ouvrir, lire, cliquer et capturer une page, sous Windows seulement |
| clean-code | `/clean-code` | audite et range le code : fichiers courts, une logique par fichier, code mort |
| clean-commits | `/commit` | découpe les changements en commits propres, un par intention |
| limited-run | aucune | lance chaque tâche avec une limite de mémoire et la ferme dès qu'elle ne sert plus |
| resource-guard | aucune | vérifie mémoire, processeur et disque avant une commande lourde, et attend s'il en manque |
| stop-resume-agents | `/stop-all`, `/resume-all` | arrête tout, sous-agents compris, et reprend plus tard là où chacun en était |
| using-git-worktrees | `/isoler` | isole un travail dans une copie de travail à part |
| writing-skills | `/creer-skill` | écrit ou corrige une skill, et la teste sur des sous-agents |

## Licence

MIT, voir `LICENSE`. Copyright (c) 2026 Florent Leterme.
