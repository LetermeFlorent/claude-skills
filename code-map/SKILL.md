---
name: code-map
description: Use when finding where something is defined or used, what calls what, mapping an unknown project before reading files one by one, looking for dead code or import cycles, or when the old graphify tool or a graphify-out folder is mentioned.
---

# Mapping a project's code

Small local map of any project, 3 files or a monorepo: definitions with line numbers, imports, and which files
mention which symbol. No model call, no network, no dependency, Python 3 standard library only. Replaces
graphify.

`<skill>` = this folder. Every query refreshes the map first, reading only files whose size or mtime changed, so
there is no build step to remember.

```
python -I "<skill>/scripts/code_map.py" build [--root DIR] [--scope SUBDIR]
python -I "<skill>/scripts/code_map.py" report
python -I "<skill>/scripts/code_map.py" find <words...> [--budget N]
python -I "<skill>/scripts/code_map.py" explain <name or file>
python -I "<skill>/scripts/code_map.py" path <a> <b>
python -I "<skill>/scripts/code_map.py" unused
```

Run from inside the project, or pass `--root`. Root = git top level, else the folder given. Flags are in `--help`.

| Command | Prints |
|---|---|
| `build` | files, symbols, edges, languages, changed files read, time. Forces a refresh. |
| `report` | biggest files, most referenced symbols (hubs), import cycles, folders, dead code. Also writes `report.md`. |
| `find` | `path:line kind name` for symbols and files matching the words (camelCase and snake_case split), with who references each. Cut at the budget (about 6000 characters). |
| `explain` | where defined, what the file uses, who references it, import neighbours. Accepts a file path. |
| `path` | shortest chain of references and imports between two symbols or files. |
| `unused` | symbols no file mentions: dead code candidates. |

## When to use it

| Situation | Use |
|---|---|
| Unknown project, about to open files one by one | `report`, then `find` |
| Who calls or uses X, what breaks if X changes | `explain X` |
| How A reaches B | `path A B` |
| Cleanup, import cycles, dead code | `report`, `unused` |
| Tiny project, one exact string to locate | grep is enough |

The map beats grep on callers, cycles, unused code and unknown projects. It does not replace reading: take
the lines it gives, then open only those files.

## Limits

What the map can and cannot tell.

1. A reference is a whole identifier token. Two symbols with the same name are not told apart, and names
   under 3 characters, very common names or names defined in more than 4 files are not linked.
2. Python is parsed with `ast`. JS, TS, Go, Rust, Java, Kotlin, C#, C and C++, PHP, Ruby, Swift, Lua, Luau and
   shell use line patterns. Any other text file is a file node only.
3. `unused` is a candidate list: entry points, tests, dunder names and index files are skipped, but names
   reached by reflection or from outside the project still show up.
4. A file edited in this run is read directly: the map is refreshed on the next query, not live.
5. Files over 1 MB, binaries and `.ia/` are left out.

## Storage

The map lives in `<root>/.ia/code-map/` (`map.json`, `report.md`). It is never committed. Delete the folder to
force a full rebuild.
