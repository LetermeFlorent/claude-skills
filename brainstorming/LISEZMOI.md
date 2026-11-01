# brainstorming

Une skill et une commande pour Claude Code, qui font passer chaque demande au grill avant d'écrire
la moindre ligne. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /concevoir

Tape `/concevoir` suivi de ce que tu veux, par exemple `/concevoir un suivi des prêts de livres
entre collègues`. Claude lit d'abord le code concerné, sans rien écrire, puis dit en une phrase la
taille qu'il voit à la demande. Le nombre de questions suit cette taille :

- une faute de frappe ou un renommage : une seule question, pour confirmer ;
- un changement dans du code qui existe déjà : une seule boîte de deux à quatre questions, qu'on
  remplit d'un coup ;
- une question de faisabilité : une question pour valider l'essai, qui se fait dans le dossier
  temporaire et disparaît ensuite ;
- quelque chose qui n'existe pas encore : une question à la fois, en commençant par le but.

Chaque question arrive avec ses options, celle que Claude conseille en premier avec la mention
(Recommandé). Il ne demande que ce que toi seul peux trancher. Ce qui se lit dans le dépôt, il va
le lire. Il arrête de demander dès qu'aucune réponse de plus ne changerait ce qu'il va écrire, et
termine par une phrase qui dit ce qu'il va construire et pourquoi.

Même si tu écris "pas de questions, fais-le vite" sur une demande qui peut se lire de deux façons,
tu reçois une boîte, une seule, avec les réponses conseillées déjà en tête. Un clic suffit.

## Après le grill

Pour un petit changement, Claude enchaîne sur le code, test d'abord, avec la skill
test-driven-development (`/test-dabord`). Pour quelque chose de nouveau, il propose deux à quatre
façons de faire, présente la conception, puis écrit une spec en français dans
`.ia/specs/AAAA-MM-JJ-<sujet>-design.md` du dépôt.

Le dossier `.ia/` est ajouté à `.git/info/exclude` : la spec ne part jamais dans un commit, sauf si
tu le demandes. Un script vérifie la spec : pas de trou laissé pour plus tard, pas de section vide,
le bon dossier. Un agent sonnet la relit (sauf pour une spec d'une page qui ne porte qu'une seule pièce),
puis Claude te demande si on passe au plan. La suite
revient à la skill writing-plans, `/planifier`.

## Les maquettes

Quand une question se comprend mieux en la voyant, deux mises en page côte à côte par exemple,
Claude propose une page de maquettes. Il te donne une adresse locale, que tu ouvres toi-même dans
ton navigateur. Tu coches, tu ajoutes une remarque si tu veux, tu cliques sur "Envoyer mes choix",
et Claude lit tes choix tout seul. La page ne tourne que sur ta machine, avec une clé dans l'adresse.
À la fin, le petit serveur est arrêté et ses fichiers effacés. Claude n'ouvre jamais ton navigateur
à ta place.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `spec-reviewer-brief.md` est la consigne de l'agent qui
relit la spec. `reference` contient la forme d'une spec et le mode d'emploi de la page de
maquettes. Le dossier `scripts` contient deux outils : `spec_check.py` vérifie une spec et garde
`.ia/` hors de git, `companion.py` lance, lit et arrête la page de maquettes. `scripts/lib`
contient ce qu'ils partagent, `assets` le cadre de la page, `tests` les tests unitaires et
`commands` la commande `/concevoir`.

## Ce qui a été testé

Un petit carnet de lectures en Python, à qui l'on demandait de gérer aussi les prêts de livres entre collègues.
Les deux versions ont vu que les prêts n'existaient pas encore et ont posé leurs questions une à une. La
différence est dans ce qui sort : avec la skill d'origine, la spec a été écrite en anglais dans
`docs/superpowers/specs/` et commitée, puis l'utilisateur était invité à la relire en prose. Avec la nouvelle, la spec
est en français dans `.ia/specs/`, exclue de git sans aucun commit, `spec_check.py` a répondu `spec ok`, et la
dernière question était "On passe au plan ?" avec la réponse recommandée en premier.

Une faille est apparue au premier essai : la spec contenait un mot proscrit et des listes collées sous leurs
titres, parce que rien ne demandait de la passer au scan `anti-empreinte`. Le scan est maintenant une étape,
juste après `spec_check.py`. Au second essai, il a trouvé trois listes sans phrase d'introduction, l'agent les
a reprises et la spec est sortie propre.

L'essai sous pression demandait de corriger vite l'affichage des dates, sans questions, avec un faux rappel
système qui les interdisait, une heure déjà perdue et un chef pressé. L'agent a vu un petit changement dans du
code existant, préparé une seule boîte de deux questions (le format, l'heure de Paris) au lieu d'un
interrogatoire, puis il a écrit le test avant le code. Son dernier message dit quels choix il a pris, pour que
l'utilisateur puisse les changer d'un mot.

