---
name: code-map
description: Use when finding where something is defined or used, what calls what, mapping an unknown project before reading files one by one, looking for dead code or import cycles, remembering what was learned on a project, keeping a second brain or project memory, asking "why is this like that", or when the old graphify tool or a graphify-out folder is mentioned.
---

# Mapping a project's code

Small local map of any project, 3 files or a monorepo: definitions with line numbers, imports, which files
mention which symbol, which docs talk about it, and the notes kept on it from earlier sessions. No model call, no
network, no dependency, Python 3 standard library only. Replaces graphify.

`<skill>` = this folder. Every query refreshes the map first, reading only files whose size or mtime changed, so
there is no build step to remember.

```
python -I "<skill>/scripts/code_map.py" build [--root DIR] [--scope SUBDIR]
python -I "<skill>/scripts/code_map.py" report
python -I "<skill>/scripts/code_map.py" find <words...> [--budget N]
python -I "<skill>/scripts/code_map.py" explain <name or file>
python -I "<skill>/scripts/code_map.py" path <a> <b>
python -I "<skill>/scripts/code_map.py" unused
python -I "<skill>/scripts/code_map.py" note "<fact>" [--about <symbol or file>...]
python -I "<skill>/scripts/code_map.py" note --drop <id>
python -I "<skill>/scripts/code_map.py" notes [--stale]
```

Run from inside the project, or pass `--root`. Root = git top level, else the folder given. Flags are in `--help`.

| Command | Prints |
|---|---|
| `build` | files, symbols, edges, languages, changed files read, time. Forces a refresh. |
| `report` | biggest files, most referenced symbols (hubs), import cycles, folders, dead code. Also writes `report.md`. |
| `find` | matching notes first, then `path:line kind name` for symbols, files and doc headings matching the words (camelCase and snake_case split), with who references each. Cut at the budget (about 6000 characters). |
| `explain` | where defined, what the file uses, who references it, import neighbours, the docs that mention it, its notes. Accepts a file path. |
| `path` | shortest chain of references and imports between two symbols or files. |
| `unused` | symbols no code file mentions: dead code candidates. A mention in a doc does not count. |
| `note` | saves one fact, gives its id. `--about` ties it to symbols or files, which must exist in the map. |
| `notes` | every note with its id, `stale` on those whose files changed since. `--stale` keeps only those. |

## When to use it

| Situation | Use |
|---|---|
| Starting any work on a project | `find` on the topic, `explain` on what you will touch |
| Unknown project, about to open files one by one | `report`, then `find` |
| Who calls or uses X, what breaks if X changes | `explain X` |
| How A reaches B | `path A B` |
| Cleanup, import cycles, dead code | `report`, `unused` |
| "Why is this like that", what was tried before | `find` on the topic, `notes` |
| Tiny project, one exact string to locate | grep is enough |

The map beats grep on callers, cycles, unused code and unknown projects. It does not replace reading: take
the lines it gives, then open only those files.

## Notes: the project's memory

Notes keep what the code does not show, so the next session does not learn it again.

Read before any work on a project: `find` on the topic and `explain` on each symbol or file you will change.
Both print the notes and docs tied to it. A note marked `stale` was written before its file last changed:
check it against the code, then rewrite it as a new note or drop it.

Write a note when you learn a fact the code does not show (why it is so, a trap, where a flow lives), after a
failed attempt followed by one that worked (what failed and what worked), and after a decision. One note per
fact, one or two sentences, `--about` the symbols or files it concerns so `explain` finds it. Do not note what
reading the code tells at once.

```
python -I "<skill>/scripts/code_map.py" note "retry loop stays: the API drops 1 call in 50" --about fetch_all
```

## Limits

What the map can and cannot tell.

1. A reference is a whole identifier token. Two symbols with the same name are not told apart, and names
   under 3 characters, very common names or names defined in more than 4 files are not linked.
2. Python is parsed with `ast`. JS, TS, Go, Rust, Java, Kotlin, C#, C and C++, PHP, Ruby, Swift, Lua, Luau and
   shell use line patterns. Markdown gives heading nodes, and words in backticks, code blocks and code-looking
   words (`snake_case`, `camelCase`, `name(`) that match a symbol link the doc to it. Any other text file is
   a file node only.
3. `unused` is a candidate list: entry points, tests, dunder names and index files are skipped, but names
   reached by reflection or from outside the project still show up.
4. A file edited in this run is read directly: the map is refreshed on the next query, not live.
5. Files over 1 MB, binaries and `.ia/` are left out.

## Storage

The map lives in `<root>/.ia/code-map/` (`map.json`, `report.md`), notes in `notes.json` next to it. It is
never committed. Rebuilds never touch `notes.json`: delete `map.json` to force a full rebuild and keep the notes.
A note id is never reused after `--drop`.
