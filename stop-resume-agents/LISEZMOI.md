# stop-resume-agents

Une skill et deux commandes pour arrêter tout le travail en cours, sous-agents compris, puis le reprendre
plus tard. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /stop-all

Claude coupe son propre travail et demande à chaque sous-agent un compte rendu : mission, ce qui est fini
et vérifié, étape en cours, fichiers touchés, ce qui reste. Un agent muet au bout de 5 minutes est arrêté,
et sa fiche est reconstruite depuis son journal (`/stop-all 10` attend 10 minutes). Tout est écrit dans
`.ia/resume.md` à la racine du dépôt, sinon dans le dossier du projet, sinon sur le Bureau. Le dossier
`.ia/` reste hors de git. Aucun commit, aucun push.

## /resume-all

Claude retrouve le dernier `resume.md`, vérifie que rien n'a bougé depuis l'arrêt (branche, fichiers des
agents) et te demande quoi faire si quelque chose a changé. Il relance ensuite chaque agent pas fini avec le
même type, le même modèle et le même effort. Le fichier n'est jamais effacé : il passe à l'état `REPRIS`.

## Le contenu du dossier

`SKILL.md` porte la procédure. `report-request.md`, `resume-template.md` et `relaunch-brief.md` sont le
message envoyé aux agents, le modèle de `resume.md` et la consigne des agents relancés. `scripts` résume les
journaux des agents, retrouve les fichiers de reprise et vérifie qu'un `resume.md` est complet. `tests`
couvre les parties pures de ces scripts.
