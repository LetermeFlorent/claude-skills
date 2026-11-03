---
description: Commite proprement les fichiers de cette session, un commit par intention, puis pousse la branche.
argument-hint: "[fichiers, dossier ou intention a commiter]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion
---

Charger la skill `clean-commits` et suivre sa procedure en mode `/commit`. Precision : $ARGUMENTS. Si elle n'est pas vide, elle restreint les fichiers ou oriente le message, sans jamais ajouter un fichier d'une autre session sans poser la question. Reponse finale en francais, courte : chaque commit (hash, titre), le push, les fichiers laisses de cote et pourquoi.
