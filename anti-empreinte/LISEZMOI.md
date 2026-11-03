# anti-empreinte

Une skill et une commande pour Claude Code qui empêchent un texte, un code ou un dépôt de trahir qu'une IA l'a produit. Installation : voir `INSTALL.md` à la racine du dépôt.

## En écrivant

Dès que Claude écrit un fichier, il suit la page de `reference` qui correspond (prose, code, interface, documents et images, git), puis passe le scan sur ce qu'il a écrit. Le noyau des six interdits et la règle zéro (le travail passe avant la forme) sont en tête de `SKILL.md`. Avant de rendre, il relit aussi son texte comme un inconnu qui chercherait ses tics à lui, et réécrit chaque phrase sortie dans sa forme habituelle : `reference/models.md` liste les tics connus des modèles Claude (Opus, Sonnet, Haiku, jusqu'à la 5.5) et Qwen (famille 3, dont 3.6 et 3.8).

## /anti-empreinte

Tape `/anti-empreinte` suivi d'un fichier, d'un dossier ou d'un dépôt. Le scan liste chaque trace avec sa ligne. Ce qui est sans risque (guillemets courbes, caractères invisibles, espaces insécables, filets entre sections) est corrigé par le script avec `--fix`. Le reste est corrigé à la main (tiret cadratin, emoji, Title Case, tournures typiques, restes de chatbot) ou te est demandé (commit déjà poussé, fichier d'outil suivi par git, branche au nom d'un outil).

Les chaînes du code, les fichiers de traduction, les données et les blocs de code ne bougent pas : ce sont des valeurs.

## Historique git

À la première commande git d'un dépôt, Claude lance `history.py`. Les commits pas encore poussés de la branche en cours perdent leurs lignes de signature, l'auteur reste. Les commits déjà poussés ne sont jamais réécrits : Claude donne leur nombre et leurs identifiants, puis demande. Un co-auteur qui est une personne reste, même s'il s'appelle Claude.

## Ce qui ne se retire jamais

La provenance d'une image générée (C2PA, IPTC, données Stable Diffusion ou ComfyUI, SynthID) : Claude dit qu'elle est là.

## Le dossier

`SKILL.md` porte la procédure, `reference` les listes et les règles, `scripts` le scan (`scan.py`) et l'historique (`history.py`), `tests` les motifs, `commands` la commande.
