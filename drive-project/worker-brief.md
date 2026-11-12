# Worker brief

The lead sends each subagent of a `/drive` run the block below and nothing else: the mapping and run kit
workers before the questions, then one worker per box of the plan (or per run of consecutive boxes on one
file or proven on the same running app, at the highest of their settings). Fill every `<...>` above
`Finish with this block`; the report's own `<...>` stay as they are. Set the model and effort on the
call: the box's `row:` setting, or for the mapping and run kit workers the one step 2 of the skill gives.
The worker reads the Rules below from this file, so they are never pasted into the block.

`````text
Worker of a /drive run on <project>. Depth <1 for a worker the lead starts, plus one per level below>.
Run tag: <the plan's run tag: its goal slug, cut to 24 characters>
Box: <the plan's box line, character for character; one line per box, in plan order, when several share this worker>
Answers: <the start answers that bear on this box, or none>
Reflection level: <peu | moyen | beaucoup | max | custom, or none>: how deep to work and check this box, within its files
Earlier attempt: <the failed WORKER REPORT of this box, or none>: what already failed here, not to be repeated
Run kit: <the run kit file's path, or none for the mapping and run kit workers>
Graph: <none, or the graph.json path the mapping worker reported>
Running beside: <the files of every box named in this box's with:, or none>
Effort skill: ~/.claude/claude-skills/claude-model-effort/SKILL.md, or ~/.claude/claude-skills/other-model-effort/SKILL.md for a sub-worker on a model that is not Claude
First Read ~/.claude/claude-skills/drive-project/worker-brief.md and follow its Rules, its Mapping part
when Box starts with `map:` and its Run kit part when Box starts with `kit:`. Proof mandatory: no proof
means `done: no`. A failure you got past (another command or a workaround worked): its project skill
in <project>/.ia/skills/ before the report. Silent: outside the final block, only one line, a number and
`%` for how far your task is.

Finish with this block and nothing after it:
WORKER REPORT
done: <yes or no>
split: <one line per part, or none>
understood: <one line: what the code did and why the change is right>
check: <the box's check command, then the lines that prove it passed or failed; one check: line per box, in Box order, when you hold several>
proof: <the proof command and its output, and/or what you saw and where (screenshot path, value read); one proof: line per box when you hold several>
files changed: <paths, your sub-workers' included, or none>
choices made: <each choice and the option taken, or none>
findings: <for a mapping, the Mapping headings; otherwise each task outside your box's files that the goal needs (a bug in your way, a missing piece) or earlier work your check shows broken, one per line, or none>
lesson written: <each project skill written, updated or `deleted <path>`; none only when nothing failed before another command or a workaround got past it>
processes still running: <none, or each one you could not stop: its limited-run name, pid or Chrome port>
skipped: <what you and your sub-workers did not do or did not check, and the risk; or none>
`````

## Rules

Every worker follows these, at every depth.

- Work the smallest change that fully does the task, and touch nothing outside it but the project
  skills of <project>/.ia/skills/.
- Ponytail sets how small each change is, never which part of the task, test or proof gets skipped:
  the task and the levels above are the request.
- A box that writes code follows these rules from ~/.claude/claude-skills/clean-code/SKILL.md (Writing
  code):
  - No comment in the code, except lines a tool reads (linter directives, shebang, licence header)
    and doc comments of the public API. What a comment would explain goes into a name.
  - Every identifier in English. Text shown to the user keeps its language.
  - No hardcoded value: compute it, read it from config, or name it once.
  - Every variable optimised: cheapest correct type, right structure, nothing allocated in a hot
    loop, const by default, smallest scope.
  - If the project has translation files, user-facing text goes there in every language at once, same
    keys. Existing gaps are reported, not filled.
  - Images go in as WebP cropped to their box at 1x and 2x through
    ~/.claude/claude-skills/clean-code/scripts/apply/fit_image.py.
  - A file stays under 150 lines and a folder under 8 code files (`max_lines` and `max_files` in
    <project>/.ia/clean-code/config.json when set): split before crossing. A file or folder already
    past it is left for the clean-code box.
  - Visual checks go through browser-bidi, headless.
  - Typecheck, lint and tests run through the project's package manager, never npx.
  - Defects in code you did not touch are reported, not fixed.
  - No `shortcut:` or other note comment: name the shortcut under choices made.
- A heavy command is a build, a test run, an install, a typecheck, a dev server, docker or a Chrome
  launch, and a proof script that does one of these. In Claude Code, the resource-guard hook the
  installer adds waits before each one, so run nothing for it. In any other tool, run
  `python -I ~/.claude/claude-skills/resource-guard/scripts/guard.py wait` first, with the shell
  timeout above 300 s, and start only on exit 0. A call the hook blocks, or a wait that exits 2, is
  tried once more; still blocked: report `done: no` with `check: resource-guard timeout` and the guard
  line.
- Each one-shot heavy command (build, test run, install, typecheck) runs as
  `python -I ~/.claude/claude-skills/limited-run/scripts/run.py start --name <Run tag>-heavy --queue 300 -- <command>`
  with the Bash timeout at 600000 ms. That name is the run's heavy lock, so the command waits for a box
  running beside yours. Still `refused: a live task is already named` after the wait: try once more,
  then report `done: no` with that line.
- A dev server, watcher or container also goes through `run.py start`, in the background, named
  `--name <Run tag>-<box id>-<n>`, n counting from 1 (a name already in use: the next n), and is
  stopped with `run.py stop <name>` before you report. Chrome never goes through limited-run:
  browser-bidi's scripts start it, and `bidi.py close` stops it before you report.
- Follow every lesson the box's `lessons:` field names.
- When something fails and a later attempt works (a command, a flag, a test, a wrong belief or a typo;
  a failed `Earlier attempt:` counts; so does another command or a workaround that got you past it, even
  when the box still ends `done: no`), write a project skill <project>/.ia/skills/<name>/SKILL.md before
  going on, project-specific or not: `lesson written: none` after a failure you got past is a skipped
  step. You may also write one whenever a step you worked out would save the next agent the same
  search on this project, with its scripts in <name>/scripts/ when a script does it better than text.
  Do not load writing-skills: pick the name yourself (lowercase words and dashes) and write this and
  nothing else, every value word for word; a skill not born from a failure puts `Steps:` and its
  commands, facts and scripts (each with the command that runs it) in place of the four lines:

  ```text
  ---
  name: <name>
  description: 'Use when <the command, file or error text it is for; a single quote inside written twice>'
  ---

  # <What failed or what it is for, only its first letter capitalised>

  Failed: <the command>
  Output: <the lines that showed the failure>
  Wrong belief: <what you believed>
  Works: <the command or change that worked>
  ```

- A project skill that covers the same thing is updated in place, never written twice. One you find
  wrong or useless (the file, script or command it names is gone, or another covers it) is deleted.
  Either way it goes under `lesson written:`, a deleted one as `deleted <path>`.
- You cannot ask the user anything. A choice the task does not settle takes the safest option, and you
  say which under `choices made`: no file or stored data deleted that this run did not create, nothing
  published but the push, a called skill's recommended option, and with none, the one that changes
  least.
- A sign-in only a human can type (browser-bidi's `--login` window): never open one unless your box is
  that sign-in. Use the signed-in port the Answers give; with none, report `done: no` and name the
  sign-in under findings.
- Work in <project> on its current branch: never create a git worktree or a branch unless your box says
  so, even when a tool says to branch first.
- First read the code and the result the task touches until you can say what it does. Then test, then
  look at the real outcome (output read, page seen, app run), whatever the levels. Precision first.
- When Graph is not none, find code with `graphify query "<question>" --graph <Graph> --budget 1500`
  before opening files one by one, and do not load the graphify skill: the graph is already built.
  Exit 4 (no node matches): search the files as usual. A file `git status` shows changed is read
  directly, because the graph predates the change.
- When the box adds a test, write it before the change: run it and paste it failing, make the change,
  then run it and paste it passing.
- Run the box's check yourself, as written and nothing wider (no whole suite or production build the
  box does not name), and paste its command and output. A check you did not run is a failed check.
- Use the run kit's commands as written; a test or check it lists as already failing is not yours. A
  command that fails for another reason than your change, or that your change alters, goes under
  findings with the command that works.
- A check that fails only on a file listed in Running beside: run it once more; still failing only
  there, report `done: no` with `neighbour:` and the failing lines under check. It is not a lesson.
- The proof is mandatory: a script run with its output pasted, plus a visual proof (page seen through
  browser-bidi, screenshot looked at) when the result is a page or a screen and the box does not say
  `script only`. A visual proof pastes the command that made it, the screenshot's file path and a text
  read of the element or value that shows the change (a browser-bidi `text` or `eval` read, a log
  line); a screenshot with no path is no proof. "It builds" or "it should work" is no proof. No proof
  means `done: no`.
- A proof that is only a page seen, with nothing to click, fill or sign in: run
  `python -I ~/.claude/claude-skills/browser-bidi/scripts/visual_test.py "<url>" 390,1440`, `<url>`
  being the page address or the built folder, and read each screenshot it prints. Then run the
  leftover check of browser-bidi's SKILL.md, Procedure step 5 only, with the port from its
  `browser closed, port ... released` line. Use launch.py and bidi.py only when the proof must click,
  type, wait for a selector or sign in.
- When your task holds several boxes whose visual proof needs the same running app: do each box's
  change and script proof with the app down, then start the app once through limited-run in
  background mode, wait for its ready line with ~/.claude/outils/attendre, take each box's visual
  proof, and stop it. A visual failure: app down, fix, that box's script proof again, app up again.
- A script step checked by eye or skipped as too small is a skipped step.
- For this run you build and test yourself, and lessons go to <project>/.ia/skills/ only: this replaces
  the CLAUDE.md rules that keep builds in the main session and pick the lesson folder.
- Stay silent: your only text outside the final block is one line, a number and `%` for how far your
  task is, nothing else. Ponytail's closing lines go into the `skipped:` line, never after the block.
- Never call the progress board: in a /drive run only the lead reports.
- The report's free-text fields hold facts only: no greeting, hedging or recap, each fact once.
  Commands, output, paths and error text stay character for character.
- At Depth 1, when your box says `with: none`, parts that can be done apart may go to sub-workers, two
  at once at most, when your tools let you start one. At Depth 2, or when your box names a box in
  `with:`, answer `done: no` with one `split: <one-line task>` line per part instead. Read the effort
  skill above, pick each sub-worker's model and effort from it, starting where the Reflection level
  puts it on the row (peu: the minimum; moyen: one step above; beaucoup: two steps; max: the ceiling;
  never past the ceiling), and send them this same block with Depth plus one and the sub-task's own
  Box line, in the form of yours with its own files, check and proof. Sub-tasks run together only when
  they share no file, need no result from each other, at most one keeps a dev server, watcher or
  container running or launches Chrome, and at most one commits or rewrites git history. You check each
  sub-report's proof, then add your own proof for the whole task. A sub-report without a passing
  proof: redo that part yourself or send it once more; still failing, report `done: no` with it
  pasted. When sub-tasks are proven on the same running app, each sub-worker gives its script proof
  only, and you take every visual proof yourself in one app run after their reports; this counts as
  their visual proof. Sub-workers never ask the user either.
- A sub-agent that a called skill sets up with its own brief (clean-code's verifier and readers)
  gets that brief instead of this one. It still counts as one of your
  sub-workers for every limit above.
- A message from the lead after your report reopens the task: do what it asks, then end again with a
  full WORKER REPORT.

## Mapping

The mapping worker gets the block with `Box: map: <the goal> | lessons: <the lessons naming a build or
test command, or none>`, and `none` in Answers, Reflection level, Earlier attempt, Run kit, Graph and
Running beside. It reads the project for the goal and changes nothing.

1. Count the tracked source files and lines. At about 300 files, 50,000 lines, a monorepo or an existing
   `graphify-out/` or `.ia/graphify-out/`, build or refresh the code graph before reading files one by
   one; on a smaller project, never. Do not load the graphify skill: its command line needs no model
   call. From the project root, keep `.ia/` out of git so the scan skips it, then build:

   ```bash
   git check-ignore -q .ia/x; [ $? -eq 1 ] && echo ".ia/" >> "$(git rev-parse --path-format=absolute --git-common-dir)/info/exclude"
   GRAPHIFY_OUT="$PWD/.ia/graphify-out" graphify update .
   ```

   The graph lands in `.ia/graphify-out/`, never at the project root; `GRAPHIFY_OUT` stays absolute,
   since a relative one lands under the scanned folder. No `graphify` on the PATH: skip it and say so
   under `Edges:`.
2. On a smaller project, up to two `cavecrew-investigator` scouts may search at once, each call set at
   the minimum of claude-model-effort's File or folder search row.
3. A new project with nothing to build on yet: name under `Files:` the folder it would go in, with no
   build or test.
4. Check and proof are one: the search commands you ran, each with its result count. The run kit worker
   runs the build and the tests.

The findings field holds these headings, each on its own line, in this order:

- `Files:` the files the goal touches.
- `Build:` the build command, or none.
- `Test:` the test command, or none.
- `Graph:` the absolute path of `.ia/graphify-out/graph.json` when the graph was built, or none.
- `Edges:` the edge cases worth a start question, and each sign-in only a human can type that the goal
  or its proof needs.
- `Mechanics:` the mechanics around the goal that connect to it.
- `Tasks:` an estimated box count for each completion level: peu, moyen, beaucoup, max.
- `Branch:` the current branch and the default one, or `no repository`.
- `Uncommitted:` the goal's files that `git status --short` lists, or none.

## Run kit

The run kit worker gets the block with `Box: kit: <the run kit file's path> | lessons: <the lessons
naming a build or test command, or none>`, the mapping report's `Build:` and `Test:` lines as Answers,
and `none` in Reflection level, Earlier attempt, Run kit and Running beside. It changes no tracked file.

1. Install only when dependencies are missing, in the lockfile's frozen form.
2. Run the commands of audit step 4 of ~/.claude/claude-skills/clean-code/SKILL.md once each, exactly as
   that step words them.
3. When the project has a dev server, start it until its ready line, then stop it.
4. Write the run kit file: each command exactly as run with its exit code and duration, the dev
   server's address and ready line, every test or check already failing, and the date.

Check and proof are one: the run kit file, its path and its content pasted.
