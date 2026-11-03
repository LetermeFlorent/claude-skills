# clean-code

Une skill et une commande pour Claude Code. Installation : voir `INSTALL.md` à la racine du dépôt.

## Usage

`/clean-code` suivi d'un dossier, d'une application ou d'un fichier. Sans argument, Claude demande
la portée. La skill se déclenche aussi sur une demande d'audit ou de rangement, ou quand un fichier
ou un dossier est devenu trop gros.

L'audit ne touche à rien avant ta réponse. Un script mesure ce qui se compte (taille des fichiers et
des dossiers, code mort, commentaires, noms français, valeurs en dur, textes hors traduction,
images, traces d'IA, secrets), Claude lit le reste, et un agent neuf confirme ou rejette chaque
constat. La note sur 20 sort d'un script, avec des plafonds : secret 5, build cassé 8, erreur avalée,
code de test livré ou signature d'IA 10.

Sous 20, Claude écrit un plan par étapes, le fait vérifier, puis te demande : tout le plan, les
étapes sûres seulement, ou rien. Chaque étape est commitée par `clean-commits`, jamais sur des tests
rouges, jamais de push.

## Règles d'écriture

Pour tout code écrit par la skill : aucun commentaire, des noms en anglais, pas de valeur en dur
évitable, des textes dans les fichiers de traduction, des fichiers sous 150 lignes, des images en
WebP en 1x et 2x.

## Fichiers

Chaque passage va dans `.ia/clean-code/` à la racine du projet (exclu de git). Les seuils se
règlent dans `.ia/clean-code/config.json`. `SKILL.md` porte la procédure, `reference/` les règles
détaillées, `scripts/` les mesures, `tests/` les tests des parties pures.
