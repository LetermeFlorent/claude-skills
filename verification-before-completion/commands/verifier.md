---
description: Verifie une affirmation, un fichier ou une tache en lancant les controles qui la prouvent ou la contredisent.
argument-hint: "[affirmation, fichier ou tache a verifier]"
allowed-tools: Read,Bash,Grep,Glob,Skill,AskUserQuestion
---

Charger la skill `verification-before-completion` avec le tool `Skill` et suivre sa partie
Procedure. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/verification-before-completion/SKILL.md`, ou
`~/.claude/skills/verification-before-completion/SKILL.md` quand la variable est vide, et
l'appliquer pareil.

Cible donnee : $ARGUMENTS. Si elle est vide, lister les affirmations de succes faites ou laissees
entendre pendant la session et les verifier une par une. Si c'est une affirmation, trouver la commande
qui echouerait si elle etait fausse. Si c'est un fichier, le controler (scan anti-empreinte, mesure
clean-code, tests qui le couvrent). Si c'est une tache, relire la demande ligne par ligne et verifier
chaque ligne.
