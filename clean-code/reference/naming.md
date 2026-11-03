# Rules 7 and 15: names

An identifier is a variable, function, class, constant, file, folder, CSS class, config key or
translation key. Text shown to the user is content and keeps its language.
`checks/files/names.py` and `checks/project/locales.py` find French segments; reading finds the
rest.

A casing deviation applied everywhere is the house convention: note it, leave it. `data`, `info`,
`tmp`, `flag`, `value`, `manager`, `helper` say nothing, and one concept has one word (`user`,
`account`, `member` for the same row is drift). Names that lie about type or unit matter most: a
tick counter called `seconds`, a squared distance called `distance`, a `getUser` that writes.

## Classify before renaming

| Level | Meaning | Handling |
|---|---|---|
| safe | never leaves the code (locals, private fields) | rename freely |
| boundary | crosses a protocol shipped in one piece (CSS class read from JS, DOM id, event name, API field both sides own) | both sides in one commit |
| breaking | written on someone's disk or in other code (config keys, localStorage keys, database columns, public API, env variables, CLI flags) | only behind a legacy alias |
| name-derived | feeds the logic (routing by substring, convention over configuration, regex over identifiers) | reread the logic, then rename |

A rename correct on every reference can still change behaviour: `if (name.includes("admin"))` sends
a page elsewhere once `adminPanel` becomes `controlPanel`. Grep the new name against every filter on
names. Boundaries hide: reflection and serializer fields, `"prefix." + name` building translation
keys, payload fields as strings, `data-*` attributes, cookies, URL paths, slugs.

## Glossary and order

Start from the English the project already ships (its English locale file outranks any word you
invent); settle contradictions in the same commit. The glossary goes in the plan. Safe renames
first, then the suite; boundary renames next, both sides per commit; breaking ones stop at the plan
with a migration and alias, or are left as is when no alias is possible in a project with users.

Never touched: locale values and user-facing prose, names imposed by a framework or outside API
(overrides, decorator targets, keys a library reads by name).
