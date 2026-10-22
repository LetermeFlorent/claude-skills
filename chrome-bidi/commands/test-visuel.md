---
description: Capture une page en largeur telephone et ordinateur, mesure chaque image, sans fenetre, puis ferme tout.
argument-hint: "<url ou dossier local> [largeurs, 390,1440 par defaut] [--visible]"
allowed-tools: Read,Bash,Skill
---

Test visuel d'une page. Tout tourne en mode invisible : aucune fenetre ne s'ouvre sur l'ecran du
user. Une fenetre seulement si les arguments contiennent `--visible`, jamais de soi-meme, et la
question "invisible ou fenetre ?" ne se pose pas.

Arguments du user : $ARGUMENTS. Le premier est l'adresse de la page ou un dossier local (servi sur
127.0.0.1 le temps du test). Ensuite, des largeurs separees par des virgules, 390 et 1440 par
defaut. Sans argument, demander l'adresse et rien d'autre.

Charger la skill `chrome-bidi` avec le tool `Skill` et appliquer sa partie /test-visuel, etape par
etape. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/chrome-bidi/SKILL.md`, ou `~/.claude/skills/chrome-bidi/SKILL.md` quand
la variable est vide, et l'appliquer pareil.

Les captures et `images.json` vont dans `<projet>/.ia/chrome-bidi/<date-heure>/`, sinon dans
`<temp>/claude-skills/chrome-bidi/`, `<temp>` etant le dossier temporaire du
systeme. A la fin, plus aucun Chrome ni chromedriver du test ne tourne : le verifier par le port affiche.

Pas de commit, pas de push. Reponse finale en francais, quelques lignes : ce qui casse a quelle
largeur, les images a refaire, et le dossier des captures.
