See `INSTALL.md` at the root of the repository for how to install the skills.

# code-map

A small map of a project's code, for the agent to read before it opens files one by one. It works the same on a
three-file script and on a big monorepo. It never calls a model, never uses the network and needs nothing beyond
Python 3. It replaces the outside tool graphify.

## What happens

When the agent needs to find where something is defined, who uses it, or what an unknown project looks like, it
runs one of the commands. The first run reads every source file and writes a map in `.ia/code-map/` inside the
project. Every later run reads only the files that changed, so it stays fast. There is no separate build step:
each question refreshes the map first.

The agent gets short lines such as `path:line kind name`, with the files that use each name, and counts at the
end. It can also ask for a report (biggest files, most used names, import cycles, folders, dead code
candidates), the shortest chain between two names, or the list of names nobody uses.

The map also reads the project's Markdown files. Each heading becomes something the agent can find, and when a
doc names a function or a file in backticks or in a code block, asking about that function also lists the doc.

It is also the project's memory. When the agent learns something the code does not show, such as why a part is
written this way, a trap, an attempt that failed and the one that worked, or a decision, it saves a short note
tied to the code it is about. The notes stay across sessions and rebuilds. Before working on the project again,
the agent searches the map and sees those notes next to the code. If the code a note talks about has changed
since, the note is marked `stale`, so the agent checks it and then rewrites or deletes it.

Nothing is committed. Deleting `map.json` in `.ia/code-map/` only costs one full rebuild; `notes.json` next to
it holds the notes and is never rebuilt.

## Files

The folder holds the instructions, the command line, the library and the tests.

- `SKILL.md`: the instructions the agent reads.
- `scripts/code_map.py`: the command line.
- `scripts/lib/queries.py`: find, explain, path and unused.
- `scripts/lib/knowledge/`: the notes (saving, listing, deleting, the `stale` check), reading Markdown files, and
  the find and explain that add notes and docs to the answer.
- `scripts/lib/report.py`: the report.
- `scripts/lib/`: file listing (git, or a folder walk) with the cache, the per-language patterns, extraction, the
  graph, and the small algorithms (word splitting, ranking, cycles, shortest path).
- `tests/test_pure.py`: unit tests of the pure parts.
- `tests/test_memory.py`: unit tests of the notes and the Markdown reading.

## What was tested

These are the real runs, done on this machine.

- `python -I -B -m unittest discover -s tests`: 28 tests pass. They cover extraction on small samples of 13
  languages, tokens, ranking, import cycles, shortest path, the cache decision, import resolution and the unused
  list, and for the memory part: saving, listing and deleting notes, ids never reused, the `stale` mark when a
  file changes or disappears, Markdown headings and links to code, find over notes, and a doc mention that does
  not hide dead code.
- `build` on this repository (293 files, git, 75 of them Markdown): 3009 symbols, 3913 edges in 0.4 s. A second
  run read 0 changed files in 0.1 s.
- On the same repository: `note "..." --about sync_skills` saved note #1, `find stale copy` printed the note
  first, `explain sync_skills` printed the definition, `docs: code-map/README.md` and the note, and
  `note --drop 1` deleted it. `--about` on an unknown name was refused. `find what was tested` lists the
  headings of that name in the READMEs, and `unused` lists 25 candidates.
- A tiny folder with one Python file and one README: after a note on `compute`, editing the file made `notes
  --stale`, `explain compute` and `find cached` show the note as `stale`.
- The working copies in `.ia/code-map/` and the tiny folder were deleted afterwards.

Gaps: the JS, TS and other non-Python patterns were tested on short samples only, not on a large real project
of those languages. Two symbols with the same name are not told apart, and common method names (`push`, `start`)
make the "who uses it" lists noisy. A plain English word in a doc that is also a symbol name is linked only when
it sits in backticks or a code block or looks like code. Notes were tried with one session at a time, not with
two sessions writing at once. Not tested on a repository of tens of thousands of files.
