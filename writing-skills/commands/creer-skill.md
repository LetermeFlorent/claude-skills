---
description: Cree, modifie ou remasterise une skill au format du depot, testee sur des agents avant et apres l'ecriture.
argument-hint: "[nom d'une skill a modifier, lecon a garder, ou chemin de notes]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,SendMessage,AskUserQuestion
---

Charger la skill `writing-skills` avec le tool `Skill` et suivre sa partie Procedure, etape par
etape. Si le tool `Skill` ne la trouve pas, lire directement
`$CLAUDE_CONFIG_DIR/skills/writing-skills/SKILL.md`, ou `~/.claude/skills/writing-skills/SKILL.md`
quand la variable est vide, et l'appliquer pareil.

Precision donnee : $ARGUMENTS. Le nom d'une skill qui existe deja veut dire une modification : le
premier essai tourne sur la version actuelle. Une lecon, ou le chemin d'un fichier de notes, donne
une nouvelle skill tiree de cette lecon. Avec "Bureau" ou "remaster", le resultat va dans
le dossier que l'utilisateur nomme, `~/Desktop/SKILLS/<nom>/` par defaut, et la version installee reste intacte.
Vide : demander ce que la skill doit apprendre, une question a la fois.

Aucune skill n'est ecrite sans un echec vu d'abord : un agent lance sans elle, ou l'echec vecu
dans la session quand c'est une lecon. La partie "Ce qui a ete teste" du LISEZMOI s'ecrit apres
les essais, d'apres ce qu'ils ont montre.

Reponse finale courte, dans la langue de l'utilisateur : le dossier de la skill, ce que l'agent faisait sans elle, ce
qu'il a fait avec, ce qui reste non teste.
