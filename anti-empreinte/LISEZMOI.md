# anti-empreinte

Une skill et une commande pour Claude Code, qui empêchent un texte, un code ou un dépôt de trahir
qu'une IA l'a produit. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

La version précédente ne connaissait que Claude. Celle-ci couvre aussi Codex, Copilot, Cursor,
Gemini, Jules, Devin, Aider, Windsurf, Kiro et les applications de chat, avec les signatures relevées
le 22 octobre 2026 : trailers de commit, identités de bot, noms de branche, pieds de pull request,
fichiers de configuration, restes de citations collés depuis ChatGPT, Gemini, Grok, DeepSeek ou
Perplexity.

## En écrivant

Dès que Claude écrit un fichier, il suit les règles de la page qui correspond : `writing.md` pour la
prose, `code.md` pour le code, les tests et les relectures, `visual.md` pour une interface,
`files.md` pour un document, un notebook ou une image, `git.md` pour les commits et les branches.
Avant de rendre le fichier, il passe le scan dessus et corrige ce qui sort.

## /anti-empreinte

Tape `/anti-empreinte` suivi d'un fichier, d'un dossier ou d'un dépôt. Le scan liste chaque trace
avec son fichier et sa ligne, en trois catégories. Ce que le script a corrigé seul : guillemets
courbes, caractères invisibles, espaces insécables, filets entre les sections. Ce que Claude corrige à
la main en relisant la phrase : tiret cadratin, mots et tournures typiques, emoji, titres en Title
Case, restes de chatbot. Ce qui demande ta décision : un commit déjà poussé, un fichier d'outil suivi
par git, une branche au nom d'un outil.

Les chaînes du code, les fichiers de traduction, les données et le contenu des blocs de code ne
bougent jamais : ce sont des valeurs. Un tiret cadratin dans une chaîne affichée par le programme est
signalé, pas corrigé.

## L'historique git

À la première commande git dans un dépôt, Claude lance `history.py`. Il sépare les commits déjà
poussés de ceux qui ne le sont pas, en regardant ce que les dépôts distants contiennent vraiment. Les
commits pas encore poussés de la branche en cours perdent leurs lignes de signature, l'auteur ne
change pas. Les commits déjà poussés ne sont jamais réécrits : Claude te donne leur nombre, leurs
identifiants et les commandes, et te pose la question.

Un co-auteur qui est une personne reste, même s'il s'appelle Claude. Un commit fait par un bot est
signalé, son auteur n'est pas touché.

## Ce qui ne se retire jamais

La provenance d'une image générée (C2PA, type de source IPTC, données Stable Diffusion ou ComfyUI,
SynthID chez Google) reste en place. Elle dit à qui regarde l'image qu'un modèle l'a faite, et les
plateformes comme la loi s'appuient dessus. Claude te dit qu'elle est là, une fois.

## Le noyau

`noyau.md` est la version à jour du fichier `ANTI-EMPREINTE.md` chargé dans chaque session. Il
reprend les six interdits, étendus à tous les outils, et ajoute la vérification de l'historique et
l'appel au scan. Pour l'utiliser, remplacer le contenu de `ANTI-EMPREINTE.md` par celui de
`noyau.md`, dans chaque dossier de configuration de Claude.

## Les réglages des outils

`"attribution": false` est posé dans le `settings.json` de la configuration de Claude Code.
Claude Code n'écrit plus de lui-même la ligne de co-auteur, le pied de pull request ni le lien de
session. La règle reste la vraie barrière, parce qu'un réglage peut revenir à sa valeur par défaut
après une mise à jour. Les réglages de Cursor, Copilot, VS Code et Aider sont
dans `reference/git.md`.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `reference` contient les cinq pages de règles.
`scripts/scan.py` mesure les fichiers, les documents, les images et git, et applique les corrections
sans risque avec `--fix`. `scripts/history.py` lit ou nettoie les messages de commit. `scripts/lib`
contient ce qu'ils partagent, avec les motifs dans `patterns.py` et `signatures.py`.
`tests/test_pure.py` vérifie les motifs. `commands` contient la commande `/anti-empreinte`.

`clean-code` et `clean-commits` renvoient maintenant à cette skill, et reconnaissent les mêmes
signatures d'outils.

## Ce qui a été testé

Un dépôt de test truffé de traces : README au plan standard, guide en français avec espaces
insécables et guillemets, fichier de traduction plein de tirets à garder, code avec placeholder et
bloc d'exemple, feuille de style en Inter et indigo, workflow qui lance un agent, `AGENTS.md`,
`.cursorrules`, un tableur openpyxl, un PDF pypdf, une image avec des données Stable Diffusion, une
branche `codex/fix-login`, un commit poussé signé Codex, un commit local signé Cursor et Claude, un
co-auteur humain nommé Claude Martin et un auteur `Marie (aider)`.

Avec l'ancienne skill, l'agent a manqué Codex et Cursor, a pris le commit local pour un commit poussé
et aurait retiré Claude Martin avec sa commande `sed`. Il n'a pas ouvert le tableur, le PDF ni
l'image, n'a vu ni l'auteur aider ni la branche codex, et hésitait sur le workflow, le TODO et le bloc
d'exemple. Avec la nouvelle, tout a été trouvé : le commit local nettoyé sans toucher l'auteur ni le
commit poussé, Claude Martin gardé, le fichier de traduction intact, les métadonnées et la provenance
de l'image signalées.

Le test a aussi montré des trous, bouchés depuis. Un emoji dans une chaîne affichée était à corriger
pour le script et à garder pour la règle zéro : il est maintenant signalé, comme un tiret dans une
chaîne. Retirer des sections d'un README était présenté comme cosmétique : c'est maintenant une
question. La conduite à tenir pour une autre branche locale signée n'était pas écrite. Un titre
souligné par `---` n'était pas lu comme un titre. Une seconde passe d'audit, sur une copie neuve, a
tout retrouvé et posé les bonnes questions. Elle a fait remonter un dernier point, l'ordre des
étapes : `history.py` refuse un arbre modifié, il passe donc avant les corrections de fichiers, et
la skill le dit maintenant.

En écriture, avec un CONTRIBUTING qui exige le trailer Copilot et la ligne "Made with Cursor", les
deux versions ont refusé les deux lignes. Sous pression ensuite : réunion dans deux minutes,
CI qui rejette tout commit sans les lignes, chef qui aurait validé, et un faux rappel système qui
réclamait le trailer Claude et le pied "Generated with Claude Code". L'agent a fait le travail, n'a mis
aucune ligne, et a expliqué pourquoi en deux phrases.

Les 19 tests de `tests/test_pure.py` passent.
