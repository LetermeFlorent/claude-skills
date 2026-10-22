---
description: Repartit des taches independantes entre plusieurs sous-agents lances ensemble, apres avoir verifie qu'ils ne se genent pas.
argument-hint: "[les taches a repartir, ou un fichier de plan]"
allowed-tools: Read,Write,Bash,Grep,Glob,Agent,Skill,AskUserQuestion
---

Charger la skill `dispatching-parallel-agents` avec le tool `Skill` et suivre sa partie Procedure,
etape par etape. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/dispatching-parallel-agents/SKILL.md`, ou
`~/.claude/skills/dispatching-parallel-agents/SKILL.md` quand la variable est vide, et l'appliquer
pareil.

Precision donnee : $ARGUMENTS. Si elle n'est pas vide, elle dit quelles taches repartir, ou donne le
chemin d'un plan deja ecrit. Vide : partir du travail en cours dans la conversation et proposer le
decoupage. Elle ne dispense jamais du test d'independance.

Un seul agent par tache, tous envoyes dans le meme message, sonnet par defaut, jamais l'effort sans
demande. Un fichier, un port, une instance Studio, Blender ou Audacity ne sert qu'a un seul agent.
Aucun agent ne rebuild une image ni ne commite. Regarder la memoire, le processeur et le disque une
fois avant l'envoi si des commandes lourdes vont tourner. Pour tout arreter puis reprendre plus tard,
la skill `stop-resume-agents` (`/stop-all`, `/resume-all`).

Reponse finale en francais, courte : les taches confiees et ce que chaque agent a trouve, ce que la
verification finale a montre, les agents arretes, et ce qui reste a faire s'il en reste.
