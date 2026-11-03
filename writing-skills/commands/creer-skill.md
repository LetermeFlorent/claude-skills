---
description: Cree, modifie ou remasterise une skill au format du depot, testee sur des agents avant et apres l'ecriture.
argument-hint: "[nom d'une skill a modifier, lecon a garder, ou chemin de notes]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,SendMessage,AskUserQuestion
---

Precision : $ARGUMENTS. Le nom d'une skill existante veut dire une modification (premier essai sur la
version actuelle). Une lecon ou un chemin de notes donne une nouvelle skill. Avec "Bureau" ou "remaster",
le resultat va dans le dossier que l'utilisateur nomme et la version installee reste intacte. Vide :
demander ce que la skill doit apprendre, une question a la fois.

Charger la skill `writing-skills` avec le tool `Skill` et suivre sa procedure.

Reponse finale courte, dans la langue de l'utilisateur : le dossier, ce que l'agent faisait sans la skill,
ce qu'il a fait avec, ce qui reste non teste.
