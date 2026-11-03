# limited-run

Plusieurs agents travaillent en même temps sur le même PC. Chaque programme qu'ils lancent (serveur de
développement, surveillance de fichiers, tests, compilation) prend de la mémoire et du processeur aux autres, et
un serveur oublié continue pendant des heures. Cette skill apprend à l'agent à lancer chaque programme avec une
limite de mémoire et une priorité basse, à le noter, puis à l'arrêter dès qu'il ne sert plus. Pour l'installer,
voir `INSTALL.md` à la racine du dépôt.

## Ce que fait l'agent

Il passe par `scripts/run.py start -- <commande>` pour tout ce qu'il lance. Par défaut la limite vaut la moitié
de la mémoire libre, entre 512 et 4096 Mo. Sous Windows, elle couvre le programme et tout ce qu'il lance à son
tour, et si le lanceur meurt, tout s'arrête avec lui. Sous Linux et macOS, elle s'applique à chaque programme
séparément.

Quand le résultat est là (la page s'affiche, les tests sont passés), il arrête la tâche. Avant de rendre la
main, il affiche la liste des tâches encore en cours avec `run.py list` et les arrête avec `run.py stop`. Il ne
touche jamais à un programme qu'il n'a pas lancé lui-même avec cet outil : il appartient peut-être à une autre
session.

## Les autres agents

Claude Code lit la skill tout seul. Pour Codex CLI, Gemini CLI ou Qwen Code, il suffit d'ajouter une ligne dans
leur fichier d'instructions (`AGENTS.md`, `GEMINI.md`, `QWEN.md`) qui renvoie vers `SKILL.md`. La phrase à
copier est dans `SKILL.md`.

## Le contenu du dossier

`SKILL.md` porte les règles. `scripts/run.py` lance, liste et arrête les tâches, avec ses morceaux dans
`scripts/lib`. `tests/test_pure.py` vérifie les calculs et lance de vrais programmes sur la machine : code de
sortie, limite de mémoire dépassée, priorité basse, arrêt de toute l'arborescence.
