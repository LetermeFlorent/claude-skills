# Start brief

Read only by `map:` and `kit:` workers of a `/drive` run, besides Rules of `worker-brief.md`. `<repo>`:
same folder as there.

## Mapping

Mapping worker gets block with `Box: map: <the goal> | lessons: <the lessons naming a build or test command,
or none>`, and `none` in Answers, Reflection level, Earlier attempt, Run kit, Graph and Running beside.
Reads project for goal, changes nothing.

1. Any project size: build code map before reading files one by one, then find goal's code with its
   `find`, `explain` and `report` commands (code-map skill, Commands). From project root, keep `.ia/` out
   of git first:

   ```bash
   git check-ignore -q .ia/x; [ $? -eq 1 ] && echo ".ia/" >> "$(git rev-parse --path-format=absolute --git-common-dir)/info/exclude"
   python -I "<repo>/code-map/scripts/code_map.py" build --root "$PWD"
   ```

   Map lands in `.ia/code-map/`, never committed. Build fails: say so under `Edges:`, search files as
   usual.
2. New project with nothing to build on yet: name under `Files:` folder it would go in, no build or test.
3. Check and proof are one: search commands you ran, each with result count. Run kit worker runs build and
   tests.

Findings field holds these headings, each on own line, in this order:

- `Files:` files goal touches.
- `Build:` build command, or none.
- `Test:` test command, or none.
- `Graph:` absolute project root when code map was built, or none.
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
