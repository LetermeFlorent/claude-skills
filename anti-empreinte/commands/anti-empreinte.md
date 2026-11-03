---
description: Cherche et retire les traces d'IA d'un fichier, d'un dossier ou d'un depot.
argument-hint: "[fichier, dossier ou depot]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion
---

Charger la skill `anti-empreinte` et suivre sa partie `/anti-empreinte <target>`. Cible : $ARGUMENTS, ou le dossier courant si vide (le dire). Reponse finale en francais, courte : une ligne par correction, puis ce qui reste avec fichier et ligne.
