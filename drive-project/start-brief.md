# Start brief

Read only by `map:` and `kit:` workers of a `/drive` run, besides Rules of `worker-brief.md`. `<repo>`: same
folder as there.

## Mapping

Mapping worker gets block with `Chain: map: <the goal>`, `none` in every other field. Reads project for goal,
changes nothing.

1. Count code files (`git ls-files | wc -l`, or `rg --files | wc -l` without git). Over 50: build code map
   before reading files one by one, then find goal's code with its `find`, `explain` and `report` commands.
   From project root, keep `.ia/` out of git first:

   ```bash
   git check-ignore -q .ia/x; [ $? -eq 1 ] && echo ".ia/" >> "$(git rev-parse --path-format=absolute --git-common-dir)/info/exclude"
   python -I "<repo>/code-map/scripts/code_map.py" build --root "$PWD"
   ```

   50 or fewer, or build fails (say so under `Edges:`): search with `rg`.
2. Lessons of earlier runs: `rg -H '^description:' <project>/.ia/skills/*/SKILL.md`, one call; read a whole
   skill only when its line names a command, file or error of the goal.
3. New project with nothing to build on: name under `Files:` the folder it would go in, no build or test.
4. Check and proof are one: search commands you ran, each with result count.

Findings field holds these headings, each on own line, in this order:

- `Files:` files goal touches.
- `Build:` build command, or none.
- `Test:` test command and how to run one test file, or none.
- `Graph:` absolute project root when code map was built, or none.
- `Lessons:` path of each project skill bearing on goal, with the command, file or error it names, or none.
- `Edges:` edge cases worth a start question, and each sign-in only a human can type that goal or its proof
  needs.
- `Mechanics:` mechanics around goal that connect to it.
- `Chains:` features goal splits into that share no file, one per line, with files; then estimated box count
  for each completion level: peu, moyen, beaucoup, max.
- `Branch:` current branch and default one, or `no repository`.
- `Uncommitted:` goal's files that `git status --short` lists, or none.

## Run kit

Run kit worker gets block with `Chain: kit: <the run kit file's path>`, mapping report's `Build:`, `Test:` and
`Lessons:` lines as Answers, `none` in other fields. Changes no tracked file.

1. Install only when dependencies missing, in lockfile's frozen form.
2. Run commands of audit step 4 of `<repo>/clean-code/SKILL.md` once each, exactly as that step words them,
   independent ones at the same time in background.
3. Project has a dev server: start it until its ready line, then stop it.
4. Write run kit file: each command exactly as run with exit code and duration, the one-file test command,
   dev server's address and ready line, every test or check already failing, and date.

Check and proof are one: run kit file, its path and content pasted.
