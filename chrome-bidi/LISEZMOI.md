# chrome-bidi

La skill qui pilote Chrome sur ta machine, refaite en Python, et une commande `/test-visuel`.
Pour l'installer, voir `INSTALL.md` à la racine du dépôt.

## Rien ne s'affiche

Chrome tourne sans fenêtre, pour toute tâche, tout test et toute capture. Claude ne demande plus
"invisible ou fenêtre ?" au début de chaque tâche. Une fenêtre ne s'ouvre que si tu le demandes,
avec `--visible`, par exemple pour regarder Claude naviguer ou pour te connecter toi-même à un
compte Google ou Microsoft.

## /test-visuel

Tape `/test-visuel https://exemple.fr` ou `/test-visuel C:\mon\site`. Claude ouvre la page en
largeur téléphone (390) puis ordinateur (1440), fait une capture de chaque, mesure toutes les
images et ferme Chrome. Il te dit ce qui casse et quelles images sont floues (fichier trop petit
pour la place qu'il occupe) ou trop lourdes (plus de deux fois trop grandes).

D'autres largeurs se donnent à la suite : `/test-visuel https://exemple.fr 360,768,1920`.

Le résultat va dans `.ia\chrome-bidi\` à la racine du projet, un dossier par passage. Git ne le
voit pas, `.ia/` est ajouté à la liste des fichiers ignorés du dépôt sur ta machine seulement. Hors
projet, il va dans `<temp>/claude-skills/chrome-bidi/`, `<temp>` étant le dossier temporaire du système.

## Le contenu du dossier

`SKILL.md` porte les règles et la procédure, en anglais. `commands\test-visuel.md` est la
commande. Le dossier `scripts` contient quatre points d'entrée : `launch.py` démarre Chrome,
`bidi.py` fait une action (ouvrir, lire, cliquer, écrire, capturer...), `measure_images.py` mesure
les images et `visual_test.py` fait le test visuel complet. Le reste est rangé dans `core`
(connexion, processus, version du pilote), `actions` et `window`. Le dossier `tests` vérifie les
petites fonctions sans lancer Chrome. Tout est en Python sans rien à installer.

`bin\chromedriver.exe` est le pilote de Chrome. Il n'est pas copié à la main : au lancement, le
script compare sa version avec celle de Chrome et télécharge le bon chez Google quand Chrome a été
mis à jour.

## Ce qui change par rapport à l'ancienne version

Chaque action reprend la même page, au même endroit, avec les formulaires déjà remplis : avant,
chaque appel rouvrait un onglet vide et rechargeait la page, d'où des boucles. Un clic
sur un élément hors de l'écran fait d'abord défiler la page jusqu'à lui. Les listes déroulantes
et les champs de formulaire ont leurs actions `select` et `fill`. Une erreur ne sort jamais en
pavé technique : une ligne qui dit ce qui a raté, une ligne qui dit comment le faire à la main.

## Ce qui a été testé

Sur une page de test locale, en mode invisible : navigation, onglets, lecture, clics, saisie,
liste déroulante, envoi de fichier, cadre intégré, alertes, captures, PDF, mode téléphone,
position et fuseau simulés, console, requêtes réseau, cookies, puis la mesure des images et
`/test-visuel` sur un dossier et sur une adresse. Après chaque fermeture, plus aucun Chrome ni
pilote du test ne tournait.

Le code est ensuite passé par la nouvelle skill clean-code, sur une copie : 11,5 sur 20 au premier
audit, 19 après les dix étapes du plan. Les deux points qui restent sont un `2` laissé en dur et
l'absence de linter. Toutes les actions ont été rejouées dans un vrai Chrome invisible après ces
changements, et les 24 tests de `tests` passent.

Pas testé : le mode fenêtre et le placement sur un bureau virtuel, faute de module
`VirtualDesktop` et parce qu'aucune fenêtre ne devait s'ouvrir chez toi.
