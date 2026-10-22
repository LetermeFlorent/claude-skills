# Shape of resume.md

resume.md is written in French, for the user to read and for /resume-all to parse. Keep the
first line, the `Etat :` line and every `## Agent <id>` heading exactly as below: /resume-all and
`scripts/resume_check.py` look for them, and the checker refuses any `<...>` of this template left
in the file. A field with nothing to say gets `aucun`, never an empty line. Verbatim blocks use four
backticks, because reports often hold three.

While answers are awaited, a field reads `en attente <agent id>`, never a bare `en attente`: the id
makes the string unique, so Edit can replace it in one section without touching the others.

`````markdown
<!-- stop-resume-agents v1 -->
# Reprise stop-all

Etat : ARRET EN COURS
Arret demande le <AAAA-MM-JJ HH:MM> (heure locale), session d'origine <session id>.
Compte Claude : <valeur de CLAUDE_CONFIG_DIR, ou ~/.claude si vide>.
Dossier de travail : <chemin absolu>. Rien n'a ete commite ni pousse par l'arret.

## Demande de depart

````text
<la demande de l'utilisateur, mot pour mot>
````

## Session principale

Ce que je faisais a l'arret : <etape exacte, fichier et ligne, derniere commande et sa sortie utile>
Fait et verifie : <liste>
Reste a faire, dans l'ordre : <liste numerotee>
Decisions prises et pistes ecartees : <liste>
Liste de taches interne : <cases faites et non faites>

## Etat des depots

Un bloc par depot touche, sortie brute :

````text
<chemin>  branche <nom>  HEAD <sha court> <sujet du commit>
<git status --short>
<git diff --stat>
<git stash list>
````

## Agent <id> : <description>

Type : <agentType>. Modele : <model>. Effort : <effort>. Profondeur : <1 ou 2, parent si 2>.
Lance le <heure>, derniere activite le <heure>.
Reponse a l'arret : <oui, a HH:MM | non, reconstruit depuis son journal | non, termine avant l'arret>
Statut : <termine | partiel | pas commence | inconnu>
A relancer : <oui | non, parce que ...>
Ordre de relance : <1, 2, ... ; apres l'agent <id> si il depend de lui ; en parallele sinon>
Fichiers qu'il possede : <une ligne par fichier, empreinte de resume_file.py hash puis chemin absolu>

### Consigne de depart

````text
<le prompt d'origine, mot pour mot, tire du digest>
````

### Son compte rendu

````text
<le bloc AGENT REPORT, mot pour mot, ou "pas de reponse">
````

### Constat de la session principale

<ce que le digest et git montrent : fichiers ecrits, dernieres commandes, sous-agents lances ;
tout ecart entre son compte rendu et le disque, ecrit en clair>

## Processus, taches de fond et outils arretes

Un element par ligne : quoi, commande exacte, dossier, PID ou port ou id, arrete comment,
comment le relancer, s'il faut le relancer. Inclut les commandes Bash de fond, serveurs,
boucles /loop, taches planifiees, workflows, instances MCP (editeur de jeu, outil 3D, editeur de son), ports
Chrome. Rien n'a tourne : `aucun`.

## Questions sans reponse

<questions posees ou a poser a l'utilisateur, ou aucun>

## Plan de reprise

1. <agent id ou session principale> : <action> (<depend de ...>)
2. ...

## Journal

- <AAAA-MM-JJ HH:MM> arret par /stop-all, session <id>, <n> agents, <n> sans reponse
`````

When the digest prints `PROMPT NOT FOUND` and neither your context nor the parent agent's digest
holds the prompt, keep that text in the block and add a line `Consigne perdue : <why>` under it.

When the stop is complete, the `Etat :` line becomes `Etat : ARRETE`. Each /resume-all appends a
`## Reprise du <date>` section above `## Journal`, a line in `## Journal`, and sets
`Etat : REPRIS le <AAAA-MM-JJ HH:MM>, session <id>`. A file taken over by a newer /stop-all of the
same session reads `Etat : REMPLACE par <chemin du nouveau fichier>`: /resume-all skips it.
