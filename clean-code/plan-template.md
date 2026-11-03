# Shape of plan.md

Written in French at `<run>/plan.md`, parsed by `scripts/plan_check.py`. Keep the first line, the
`## Etape <n> : ...` and `## Laisse tel quel` headings and the field names exactly. The checker
refuses any `<...>` left in the file.

Every confirmed id appears once: on the `Constats :` line of one step, or under `## Laisse tel
quel` with its reason. Refuted ids appear nowhere. A step holds findings of a single phase (the
Apply table of SKILL.md, a secret is phase 6) and steps follow phase order.

`Sure : oui` only when the step cannot change behaviour: a comment removed, a typo or emoji in
prose, an unused import without side effect, a constant named without moving its value. Renames,
moves, splits, deletions and error handling are `Sure : non`.

`Fichiers :` lists every path the step writes (created, edited, deleted, a moved file under both
names), never `.ia/`, `.claude/` or `CLAUDE.md`. With no test suite, `Suite :` reads `aucune` and
each `Verification :` names a command that runs the changed code, with the output it must give. A
split that would push a folder past its file limit moves the group into a new subfolder.

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

- <id> : <raison>
`````

Nothing left as is: keep the heading and write `aucun` under it.
