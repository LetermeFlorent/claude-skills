# chrome-bidi

Skill qui pilote Chrome en Python (sans rien à installer) et commande `/test-visuel`. Installation :
voir `INSTALL.md` à la racine du dépôt.

L'IA choisit seule, sans te le demander : une fenêtre visible quand quelqu'un doit voir ou agir
(connexion à un compte Google ou Microsoft, code de vérification, ou quand tu veux regarder), sans
fenêtre pour tout le reste.

`/test-visuel https://exemple.fr` (ou un dossier local, avec d'autres largeurs en option :
`360,768,1920`) ouvre la page en largeur téléphone (390) et ordinateur (1440), capture chacune,
mesure les images (floues ou trop lourdes) et ferme Chrome. Le résultat va dans `.ia\chrome-bidi\`
à la racine du projet, ignoré par git sur ta machine seulement ; hors projet, dans
`<temp>/claude-skills/chrome-bidi/`.

`SKILL.md` porte les règles. `scripts` a quatre points d'entrée (`launch`, `bidi`, `measure_images`, `visual_test`) et deux dossiers de modules (`core` pour le navigateur, la session et les processus, `actions` pour les commandes de `bidi`). `tests` vérifie les petites fonctions.
`bin\chromedriver.exe` est téléchargé au lancement quand Chrome a changé de version.

Le mode fenêtre sur bureau virtuel n'a pas été essayé, faute du module `VirtualDesktop`.
