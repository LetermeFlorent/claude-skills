---
description: Audite une portee contre les regles de clean code, rend une note sur 20, puis demande quoi corriger.
argument-hint: "[portee : dossier, application ou fichier]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,AskUserQuestion
---

Portee : $ARGUMENTS. Si vide, la demander avec `AskUserQuestion`.

Charger la skill `clean-code` et suivre Audit puis Apply. Reponse finale en francais, courte : note
avant et apres, etapes faites avec leur commit, ce qui reste et pourquoi.
