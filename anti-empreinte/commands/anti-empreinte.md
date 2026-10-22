---
description: Cherche et retire les traces d'IA d'un fichier, d'un dossier ou d'un depot, puis dit ce qui reste a decider.
argument-hint: "[fichier, dossier ou depot]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion
---

Charger la skill `anti-empreinte` avec le tool `Skill` et suivre sa partie audit, etape par etape,
sans en sauter une. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/anti-empreinte/SKILL.md`, ou `~/.claude/skills/anti-empreinte/SKILL.md`
quand la variable est vide, et l'appliquer pareil.

Cible demandee : $ARGUMENTS. Si c'est vide, prendre le dossier courant, et le dire en une ligne.

Le script corrige seul ce qui ne change pas le sens : guillemets, caracteres invisibles, espaces,
filets. Le reste se corrige a la main en relisant la ligne. Les chaines du code, les fichiers de
locales et les donnees ne bougent pas. Les commits deja pousses, l'auteur d'un commit, une branche
poussee et la provenance d'une image ne se touchent jamais : chacun se signale, et ce qui demande une
decision passe par `AskUserQuestion`.

Reponse finale en francais, courte, dans le terminal : une ligne par correction, puis ce qui reste
avec son fichier et sa ligne ou son commit. Pas de resume a la fin.
