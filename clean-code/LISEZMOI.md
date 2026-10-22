# clean-code

Une skill et une commande pour Claude Code. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## /clean-code

Tape `/clean-code` suivi de ce qu'il faut auditer : un dossier, une application, un fichier. Sans
rien derrière, Claude te demande la portée, en proposant le projet entier puis chaque dossier qui
existe vraiment.

L'audit ne touche à rien. Un script mesure d'abord ce qui se compte (taille des fichiers et des
dossiers, code mort, commentaires, noms en français, valeurs en dur, textes hors des fichiers de
traduction, images trop lourdes ou mal cadrées, traces d'IA, secrets). Pour les traces d'IA, la
grille complète est celle de la skill `anti-empreinte`, dont le scan s'ajoute à la mesure : les
signatures de tous les outils, pas seulement Claude, plus le vocabulaire et les métadonnées des
documents. Claude lit ensuite ce
qu'aucun script ne sait juger, comme un fichier qui fait deux métiers ou du code copié à deux
endroits. Au-delà de 150 fichiers de code, la lecture part chez quatre agents au plus, un par
paquet de dossiers.

Un agent neuf, qui n'a rien vu de la mesure, reprend chaque constat et le confirme ou le rejette.
Seuls les constats confirmés comptent. La note sur 20 sort d'un script, avec des plafonds : un
secret dans un fichier suivi par git bloque la note à 5, un build cassé à 8, une erreur avalée,
du code de test livré en production ou la signature d'un outil d'IA à 10.

Sous 20, Claude écrit un plan par étapes, le fait vérifier par un script, puis te pose une seule
question : tout le plan, les étapes sûres seulement, ou rien. Rien ne bouge avant ta réponse.
Chaque étape faite est commitée par la skill `clean-commits`, posée à côté : un
commit qui ne prend que les fichiers de l'étape, jamais sur des tests rouges, et jamais de push.

## En dehors des audits

Les règles d'écriture valent pour tout code écrit, audit ou pas : aucun commentaire, des noms en
anglais, aucune valeur en dur quand on peut la calculer ou la lire dans la config, des variables
au plus juste, les textes affichés dans les fichiers de traduction quand le projet en a, des
fichiers sous 150 lignes. Une image entre en WebP, découpée à la taille de sa case, en 1x et 2x.
Toute vérification à l'écran passe par la skill `chrome-bidi`, sans fenêtre visible.

## Où vont les fichiers

Tout ce que l'audit produit va dans `.ia/clean-code/` à la racine du projet, un dossier par
passage : la mesure, les constats, la note et le plan. Chaque passage est comparé au précédent.
Le dossier `.ia/` est ajouté à `.git/info/exclude`, il ne part donc jamais dans un commit. Hors d'un dépôt git, ou quand
rien ne doit être écrit dans le projet (une relecture, un dossier de skill), `measure.py --out <dossier>`
range le passage ailleurs. Les
seuils (150 lignes, 8 fichiers par dossier, 40 lignes par fonction...) se changent dans
`.ia/clean-code/config.json`.

## Le contenu du dossier

`SKILL.md` porte la procédure, en anglais. `plan-template.md` décrit le plan, `reader-brief.md`
et `verify-brief.md` sont les consignes données aux agents lecteurs et à l'agent qui vérifie.
`reference` détaille les règles longues : noms, variables, valeurs en dur, images, traces d'IA.
Le dossier `scripts` mesure, tient la liste des constats, calcule la note, vérifie le plan et
prépare les images. `commands` contient la commande, et `tests/test_pure.py` les tests des parties
qui ne touchent ni git ni le réseau : plages de lignes, mots français, traces d'IA, dossier `--out`.

## Ce qui a été testé

D'abord sans la skill, sur un petit projet piégé : clé secrète en dur, `catch {}` vide, code de
test lancé au démarrage, noms en français, fichiers trop longs. Un agent sans skill a inventé sa
propre grille et donné 8 sur 20 ; l'ancienne skill a donné 5 avec un calcul fait à la main. Avec
la nouvelle, la note est sortie du script à 5, plafonnée par le secret, et rien n'a bougé avant la
question de dose. Sous pression, quand on lui a dit que la clé était une clé de démo, l'agent a
gardé le plafond. Un autre agent, chargé d'ajouter une fonction, a suivi les règles d'écriture
sans audit : aucun commentaire, et le seuil rangé dans la config au lieu d'un 50 en dur.

Le vrai essai s'est fait sur une copie de chrome-bidi. Un premier audit a donné 14,5 et montré
trois défauts de la skill, corrigés depuis. Le second a donné 11,5, avec 35 constats confirmés par
l'agent vérificateur. Avec la réponse "Tout le plan", les dix étapes ont été appliquées, chacune
commitée par clean-commits, puis rejouées dans un vrai Chrome invisible. Nouvelle mesure : 19 sur
20. Le chrome-bidi du dépôt a reçu ces changements.

Les scripts tournent aussi sur un projet témoin dont la mesure doit rester identique d'une version
à l'autre (53 constats, inchangée), et `fit_image.py` a découpé une image à sa case en WebP 1x et
2x. Deux trous trouvés pendant les essais sont bouchés : les brouillons vont dans un dossier propre
à chaque passage, pour qu'un agent n'efface plus celui d'une autre session, et la consigne de
l'agent vérificateur se remplit avec les vrais chemins.
