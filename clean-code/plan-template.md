# Shape of plan.md

plan.md is written in French, for the user to read before the dose question and for
`scripts/plan_check.py` to parse. It lives in the run folder, `.ia/clean-code/<run>/plan.md`, and
never anywhere else in the project. Keep the first line, every `## Etape <n> : ...` heading, the
`## Laisse tel quel` heading and the field names exactly as below. The checker refuses any `<...>`
of this template left in the file.

Every confirmed finding id appears exactly once: on the `Constats :` line of one step, or under
`## Laisse tel quel` with its reason. Refuted ids appear nowhere. A finding's phase comes from its
rule, through the Apply table of SKILL.md (a secret is phase 6). A step holds findings of a single
phase, and steps follow the phase order, so the checker refuses a phase 3 step placed after a
phase 4 one.

`Sure : oui` means the step cannot change what the program does: a comment removed, a typo or an
emoji gone from prose, an unused import that has no side effect, a constant named without moving
its value. Anything that renames, moves, splits, deletes a file or touches error handling is
`Sure : non`. The answer "les sures seulement" to the dose question applies the `oui` steps only.

`Fichiers :` lists every path the step writes, separated by commas, so the commit stages those and
nothing else: created, edited and deleted paths alike, a moved file under both names. `.ia/`,
`.claude/` and `CLAUDE.md` never appear there.

With no test suite at all, `Suite :` reads `aucune` and each `Verification :` names a command
that runs the changed code, a script with its usual arguments or a headless chrome-bidi check,
with the output it must give. A split that would push a folder past its file limit moves the
group into a new subfolder.

`````markdown
<!-- clean-code plan v1 -->
# Plan clean-code

Portee : <portee mesuree>
Run : <nom du dossier du run>, note <note>/20
Suite : <commande qui lance la suite de tests>, verte au depart : <oui ou non>

## Etape 1 : <ce que l'etape change, en mots simples>

Phase : <1 a 6>
Constats : <ids separes par des virgules>
Sure : <oui ou non>
Fichiers : <chemins ecrits par l'etape, separes par des virgules>
Verification : <commande qui prouve que rien n'a casse>
Commit : <message de commit, sans attribution>

## Laisse tel quel

- <id> : <raison pour laquelle on n'y touche pas>
`````

A plan with nothing left as is keeps the heading and writes `aucun` under it.
