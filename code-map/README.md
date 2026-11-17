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

The map is never committed. Deleting `.ia/code-map/` only costs one full rebuild.

## Files

The folder holds the instructions, the command line, the library and the tests.

- `SKILL.md`: the instructions the agent reads.
- `scripts/code_map.py`: the command line.
- `scripts/lib/queries.py`: find, explain, path and unused.
- `scripts/lib/report.py`: the report.
- `scripts/lib/`: file listing (git, or a folder walk) with the cache, the per-language patterns, extraction, the
  graph, and the small algorithms (word splitting, ranking, cycles, shortest path).
- `tests/test_pure.py`: unit tests of the pure parts.

## What was tested

These are the real runs, done on this machine.

- `python -I tests/test_pure.py`: 18 tests pass. They cover extraction on small samples of 13 languages,
  tokens, ranking, import cycles, shortest path, the cache decision, import resolution and the unused list.
- `build` on this repository (279 files, git): 2540 symbols, 2943 edges in 0.4 s. A second run read 0 changed
  files in 0.1 s.
- `report`, `find push github`, `explain sync_skills`, `path` and `unused` on the same repository all ran and
  gave plausible answers. `explain sync_skills` shows the function is only used inside its own file.
- A tiny folder outside git (two Python files and a data file): build, find, path, unused and report gave the
  expected answers, and `lonely` was listed as unused.
- The working copies in `.ia/code-map/` and the tiny folder were deleted afterwards.

Gaps: the JS, TS and other non-Python patterns were tested on short samples only, not on a large real project
of those languages. Two symbols with the same name are not told apart, and common method names (`push`, `start`)
make the "who uses it" lists noisy. The `path` command found nothing between unrelated names, as it should, but
was not tried on a very large graph. Not tested on a repository of tens of thousands of files.
