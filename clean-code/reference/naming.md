# Rules 7 and 15 in detail: names

An identifier is a name: a variable, function, class, constant, file, folder, CSS class, config key
or translation key. Text shown to the user is content, never a name, and stays in its language.

`checks/files/names.py` and `checks/project/locales.py` find French segments. Reading finds the
rest: names that lie, synonyms, casing.

## What a script cannot see

A deviation from the language's casing that is applied everywhere in the project is its house
convention: note it, leave it. Alone, `data`, `info`, `tmp`, `flag`, `value`, `manager` and `helper`
say nothing, and one concept has one word (`user`, `account` and `member` for the same row is drift).

The names that pay off most are the ones that lie about type or unit: a tick counter called
`seconds`, a squared distance called `distance`, an index called `pinned` as if it were a boolean,
a function called `getUser` that writes to the database.

## Classify before renaming

A rename is dangerous when the old name is written somewhere outside the code, or when the logic
reads it. The size of the diff has nothing to do with it.

| Level | Meaning | Examples | Handling |
|---|---|---|---|
| safe | the name never leaves the code | locals, private fields, internal classes | rename freely |
| boundary | the name crosses a protocol shipped in one piece | CSS class read from JS, DOM `id`, event name, API field both sides own | both sides in one commit |
| breaking | the name is written on someone's disk or in someone else's code | config keys, localStorage keys, database columns, public API, env variables, CLI flags | only behind a legacy alias |
| name-derived | the name feeds the logic | routing by substring, convention over configuration, a regex over identifiers | reread the logic, then rename |

The fourth level is the trap: a rename correct on every reference can still change behaviour. A
router doing `if (name.includes("admin"))` sends a page elsewhere once `adminPanel` becomes
`controlPanel`. Grep the new name against every piece of code that filters on names.

Boundaries do not show in a single file. Hunt for them: fields read by reflection or a serializer,
`"prefix." + name` that builds a translation key, payload fields sent as strings, tables that copy
field names, `data-*` attributes, cookies, URL paths, slugs.

## The glossary comes before the first rename

Start from the English the project already ships: its English locale file outranks any word you
invent. When that source contradicts itself, settle it and fix the source in the same commit. The
glossary goes into the plan, it is the part a human reviews.

## Apply in stages

Safe renames first, then the suite. Boundary renames next, both sides per commit, then the suite.
Breaking ones stop at the plan: each gets its migration and its legacy alias, and the user decides.
A breaking rename with no possible alias, in a project that has users, is left as is with that
reason.

Never touched: locale values and any prose shown to the user, names imposed by a framework or an
outside API (overrides, decorator targets, keys a library reads by name), and a house convention
applied everywhere.
