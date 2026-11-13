# Start brief

Read only by `map:` and `kit:` workers of a `/drive` run, besides Rules of `worker-brief.md`. `<repo>`:
same folder as there.

## Mapping

Mapping worker gets block with `Box: map: <the goal> | lessons: <the lessons naming a build or test command,
or none>`, and `none` in Answers, Reflection level, Earlier attempt, Run kit, Graph and Running beside.
Reads project for goal, changes nothing.

1. Count tracked source files and lines. At about 300 files, 50,000 lines, a monorepo or existing
   `graphify-out/` or `.ia/graphify-out/`: build or refresh code graph before reading files one by one;
   on smaller project, never. Do not load graphify skill: its command line needs no model call. From
   project root, keep `.ia/` out of git so scan skips it, then build:

   ```bash
   git check-ignore -q .ia/x; [ $? -eq 1 ] && echo ".ia/" >> "$(git rev-parse --path-format=absolute --git-common-dir)/info/exclude"
   GRAPHIFY_OUT="$PWD/.ia/graphify-out" graphify update .
   ```

   Graph lands in `.ia/graphify-out/`, never at project root; `GRAPHIFY_OUT` stays absolute, since a
   relative one lands under scanned folder. No `graphify` on PATH: skip it, say so under `Edges:`.
2. Smaller project: up to two `cavecrew-investigator` scouts may search at once, each call at minimum of
   claude-model-effort's File or folder search row.
3. New project with nothing to build on yet: name under `Files:` folder it would go in, no build or test.
4. Check and proof are one: search commands you ran, each with result count. Run kit worker runs build and
   tests.

Findings field holds these headings, each on own line, in this order:

- `Files:` files goal touches.
- `Build:` build command, or none.
- `Test:` test command, or none.
- `Graph:` absolute path of `.ia/graphify-out/graph.json` when graph was built, or none.
- `Edges:` edge cases worth a start question, and each sign-in only a human can type that goal or its
  proof needs.
- `Mechanics:` mechanics around goal that connect to it.
- `Tasks:` estimated box count for each completion level: peu, moyen, beaucoup, max.
- `Branch:` current branch and default one, or `no repository`.
- `Uncommitted:` goal's files that `git status --short` lists, or none.

## Run kit

Run kit worker gets block with `Box: kit: <the run kit file's path> | lessons: <the lessons naming a build
or test command, or none>`, mapping report's `Build:` and `Test:` lines as Answers, and `none` in
Reflection level, Earlier attempt, Run kit and Running beside. Changes no tracked file.

1. Install only when dependencies missing, in lockfile's frozen form.
2. Run commands of audit step 4 of <repo>/clean-code/SKILL.md once each, exactly as that step words them.
3. Project has a dev server: start it until its ready line, then stop it.
4. Write run kit file: each command exactly as run with exit code and duration, dev server's address and
   ready line, every test or check already failing, and date.

Check and proof are one: run kit file, its path and content pasted.
