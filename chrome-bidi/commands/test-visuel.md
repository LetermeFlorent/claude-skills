---
description: Capture une page en largeur telephone et ordinateur, mesure chaque image, sans fenetre, puis ferme tout.
argument-hint: "<url ou dossier local> [largeurs, 390,1440 par defaut] [--visible]"
allowed-tools: Read,Bash,Skill
---

Test visuel d'une page, sans fenetre sauf si les arguments contiennent `--visible`.

Arguments du user : $ARGUMENTS. Le premier est l'adresse de la page ou un dossier local (servi sur
127.0.0.1 le temps du test). Ensuite, des largeurs separees par des virgules, 390 et 1440 par
defaut. Sans argument, demander l'adresse et rien d'autre.

Charger la skill `chrome-bidi` avec le tool `Skill` et appliquer sa partie /test-visuel. Si le tool
`Skill` ne la trouve pas, lire directement `$CLAUDE_CONFIG_DIR/skills/chrome-bidi/SKILL.md`, ou
`~/.claude/skills/chrome-bidi/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Pas de commit, pas de push. Reponse finale en francais, quelques lignes : ce qui casse a quelle
largeur, les images a refaire, et le dossier des captures.
