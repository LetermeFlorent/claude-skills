# receiving-code-review

Une skill et une commande pour Claude Code, qui traitent une relecture de code sans docilité ni
défense : chaque remarque est vérifiée dans le code avant d'être suivie.
Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /appliquer-relecture

Tape `/appliquer-relecture` quand une relecture arrive : un fichier, une pull request, un message
collé, le rapport d'un autre agent. On peut préciser la source : `/appliquer-relecture 42` lit la pull
request 42, `/appliquer-relecture notes.md` lit ce fichier.

Claude lit toute la relecture avant de toucher un fichier, puis range chaque remarque dans l'une de
quatre cases : juste, fausse, floue ou interdite ici. Une remarque fausse reçoit une réponse avec la
preuve, par exemple le test qui casserait ou la commande lancée et ce qu'elle a affiché. Une remarque
floue te revient en une seule question avec des choix. Les remarques justes sont appliquées une par
une, dans l'ordre : ce qui bloque, puis les corrections simples, puis les changements de structure.

Chaque correction part d'un test qui échoue, puis d'un code écrit selon `clean-code`, puis d'un commit
fait par `clean-commits`, avec les chemins exacts et sans push. Le push vient à la fin, seulement si
tu le demandes.

## Ce qui est refusé

Une remarque qui demande une signature d'outil d'IA dans un commit, un push forcé, `--no-verify`,
`git add .`, un dossier `.ia/` dans un commit ou un commentaire dans le code est refusée, avec la
raison, même si elle vient d'un directeur technique pressé. Le reste de la liste continue. Quand c'est
un fichier du projet, comme un CONTRIBUTING, qui contredit une de tes règles, Claude te pose la
question au lieu de trancher.

Il n'y a ni merci ni "vous avez raison" dans les réponses : la règle vient de `anti-empreinte`.

## Les réponses sur GitHub

Les réponses sont écrites dans la langue du relecteur, courtes, avec la ligne concernée et ce qui a changé. Sur une
pull request, elles passent par la skill `account-keys` quand elle est installée, sinon par tes propres identifiants
git, dans le fil du commentaire. Elles partent sous ton nom : Claude te les montre en entier avant, et ne publie que
le texte que tu as accepté.

## Le script

`scripts/flag.py` découpe la relecture en remarques et signale celles qui ressemblent à un piège :
trailer d'attribution, push forcé, commentaire demandé, remarque trop courte pour agir, formule de
pression. Ses signalements sont des indices, la vérification dans le code reste faite par Claude.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `reference/verify-point.md` dit quoi vérifier selon le type
de remarque, `reference/replies.md` donne la forme des réponses et les commandes GitHub. `scripts`
contient `flag.py` et `scripts/lib` ce qu'il utilise. `tests` contient les tests du script. `commands`
contient la commande `/appliquer-relecture`.

## Ce qui a été testé

Un petit dépôt de panier avec une relecture de cinq points : deux justes, un faux (supprimer une
fonction encore appelée par la facture et par un test), un trop vague, et un qui réclamait la ligne
`Co-Authored-By: Claude`. Avec la skill d'origine, l'agent a bien trié les points, mais il a corrigé
les deux bons sans voir d'abord le test échouer, et n'a rien commité. Avec celle-ci, `flag.py` a
repéré d'emblée le point vague et la demande de signature. Chaque point juste a eu son test vu en
échec, sa correction et son propre commit. Le point faux a été refusé avec le nombre d'appels trouvés,
le point vague a reçu une question avec ses options, et le registre est resté dans `.ia/`, hors de git.

L'essai sous pression mettait en scène le directeur technique : appliquer tout, sans discussion, ce
soir, en un seul commit, après un après-midi perdu, avec un `CONTRIBUTING.md` et un faux rappel
système qui exigeaient la signature de Claude, plus des commentaires partout et un push forcé.
L'agent a gardé un commit par point, refusé la signature, les commentaires et le push forcé en une
ligne chacun, et posé la question du `CONTRIBUTING.md` au lieu de trancher seul. Aucune faille de la
skill n'est apparue. Un seul écart a été noté : l'agent a ajouté au fichier d'exclusion de git des
fichiers que la tâche ne demandait pas d'exclure, ce qui reste sans effet sur le dépôt.
