# Spec format

A spec is read twice: by the user, who approves it, and by `writing-plans`, which turns it into
tasks. It is written in French; code names, paths, commands and identifiers stay as they are. It
follows `anti-empreinte` like any file: no em dash, no curly quote, sentence case headings, no bold
lead-in, no closing recap.

## Path and name

The spec goes to `<repo>/.ia/specs/YYYY-MM-DD-<topic>-design.md`, dated the day it is written, the
topic in lowercase words joined by hyphens: `2026-10-22-prets-de-livres-design.md`. `spec_check.py`
refuses any other place or name. A second version of the same design edits the file; a new design
on the same topic gets a new date.

## Sections

The headings below are the usual ones, in this order. Each is followed by prose or a short list
under an opening sentence. A section with nothing to say is dropped, never left empty and never
filled with "à définir".

| Heading | What it holds |
|---|---|
| `# <Sujet> : conception` | one paragraph: what is built and why, the closing sentence of the grill |
| `## Ce que l'utilisateur a demandé` | their request in their words, then the answers they gave during the grill |
| `## Ce qui a été supposé` | each choice taken without asking, so they can overturn it |
| `## Décisions` | each decision, the options dropped and why |
| `## Conception` | the units: file or module, its one job, its interface, what it depends on; then how data moves |
| `## Erreurs` | what can fail and what the person in front of the screen sees then |
| `## Tests` | what proves each requirement, at which level, with which data |
| `## Hors périmètre` | what is not built this time, said plainly |

A unit that would grow past 150 lines, or do two jobs, is split in the design already. Values that
may change (a delay, a limit, an address) are named as configuration, with their default.

## Size

As long as the design needs and no longer. A feature fits in one or two pages. A spec that runs
much longer usually holds two projects: split it and say so to the user before writing the second.

## What the check does not see

`spec_check.py` finds placeholders, empty sections, a wrong path and a tracked file. It cannot see
a requirement that reads two ways, two sections that disagree, or a part nobody asked for. Read
the spec once for those before the reviewer gets it.
