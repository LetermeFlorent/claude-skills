# stop-resume-agents

Une skill et deux commandes pour Claude Code. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /stop-all

Tape `/stop-all` pour tout arrêter. Claude coupe son propre travail, puis envoie à chaque
sous-agent une demande de compte rendu : sa mission, ce qui est fini et vérifié, l'étape en cours,
les fichiers créés et modifiés, les commandes lancées, ce qui reste à faire. Un agent qui ne
répond pas dans les 5 minutes est arrêté de force, et sa fiche est reconstruite depuis son journal.

Tout part dans `.ia/resume.md`, à la racine du dépôt (sinon dans le dossier du projet, sinon
directement dans `~/Desktop`). Le dossier `.ia/` reste hors de git et la racine du projet reste propre.
Chaque agent y a sa section avec sa consigne de départ mot pour mot, son compte rendu, et ce que
Claude a constaté sur le disque. Aucun commit, aucun push.

On peut donner un délai : `/stop-all 10` attend 10 minutes au lieu de 5.

## /resume-all

Tape `/resume-all` pour reprendre. Claude retrouve le dernier `resume.md`, dans `.ia/` ou à la
racine pour un arrêt plus ancien. Il vérifie que rien n'a bougé depuis l'arrêt (branche, fichiers
des agents), et te pose la question si quelque chose a changé. Ensuite il relance chaque agent pas
fini avec le même type, le même modèle et le même effort, et lui donne tout son contexte. Les agents
finis ne sont pas relancés.

Le fichier n'est jamais effacé : il passe à l'état `REPRIS` et garde l'historique.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. Les trois autres fichiers `.md` sont le message envoyé
aux agents, le modèle de `resume.md` et la consigne donnée aux agents relancés. Le dossier
`scripts` résume les journaux des agents, retrouve les fichiers de reprise et vérifie qu'un
`resume.md` est complet. `commands` contient les deux commandes.

## Ce qui a été testé

Un vrai arrêt suivi d'une vraie reprise, avec trois agents factices : tous ont répondu, l'un a
repris sa tâche là où il s'était arrêté, un autre a été remplacé par un nouvel agent qui a fini le
travail sans rien faire en double. Les scripts ont aussi été passés sur des cas tordus : journal
abîmé, fichier introuvable, `resume.md` qui ne vient pas de la skill, numéro de session absent.

Le passage dans `.ia/` a été essayé sur des dépôts jetables. `/pause`, `/stop` et devflow y
écrivent leur fichier, `.ia/` part dans le fichier exclude du dépôt et rien n'est commité. La
reprise lit encore un `PAUSE.md` resté à la racine, et `/resume-all` trouve aussi bien
`.ia/resume.md` qu'un ancien `resume.md` à la racine.

`/stop` (arrêt avec commit et push) et `/pause` (fichier `.ia/PAUSE.md`) existent toujours à côté.
`/stop` écrit son `RESTE-A-FAIRE` dans `.ia/` lui aussi, et ne le commite jamais.
