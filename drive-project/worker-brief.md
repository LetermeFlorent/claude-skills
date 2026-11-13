# Worker brief

Lead sends each subagent of a `/drive` run the block below and nothing else: mapping and run kit workers
before questions, then one worker per plan box (or per run of consecutive boxes on one file or proven on
same running app, at highest of their settings). Fill every `<...>` above `Finish with this block`,
`<repo>` as absolute claude-skills folder; report's own `<...>` stay as they are. Set model and effort on
call: box's `row:` setting, or for mapping and run kit workers the one skill step 2 gives. Worker reads
Rules below from this file, so they are never pasted into block.

`````text
Worker of a /drive run on <project>. Depth <1 for a worker the lead starts, plus one per level below>.
Run tag: <the plan's run tag, character for character>
Box: <the plan's box line, character for character; one line per box, in plan order, when several share this worker>
Answers: <the start answers that bear on this box, or none>
Reflection level: <peu | moyen | beaucoup | max | custom, or none>: how deep to work and check this box, within its files
Earlier attempt: <the failed WORKER REPORT of this box, or none>: what already failed here, not to be repeated
Run kit: <the run kit file's path, or none for the mapping and run kit workers>
Graph: <none, or the graph.json path the mapping worker reported>
Running beside: <the files of every box named in this box's with:, or none>
Effort skill: <repo>/claude-model-effort/SKILL.md, or <repo>/other-model-effort/SKILL.md for a sub-worker on a model that is not Claude
First Read <repo>/drive-project/worker-brief.md and follow its Rules; when Box starts with `map:` or
`kit:`, also Read <repo>/drive-project/start-brief.md and follow its Mapping or Run kit part. Proof
mandatory: no proof means `done: no`. A failure you got past (another command or a workaround worked): its
project skill in <project>/.ia/skills/ before the report. Silent: no text outside the final block.

Finish with this block and nothing after it:
WORKER REPORT
done: <yes or no>
split: <one line per part, or none>
understood: <one line: what the code did and why the change is right>
check: <the box's check command, then the lines that prove it passed or failed; one check: line per box, in Box order, when you hold several>
proof: <the proof command and its output, and/or what you saw and where (screenshot path, value read); one proof: line per box when you hold several>
files changed: <paths outside .ia/, .claude/, .cursor/, .aider* and CLAUDE(.local).md, your sub-workers' included, or none>
choices made: <each choice and the option taken, or none>
findings: <for a mapping, the Mapping headings; otherwise each task outside your box's files that the goal needs (a bug in your way, a missing piece) or earlier work your check shows broken, one per line, or none>
lesson written: <each project skill written, updated or `deleted <path>`; none only when nothing failed before another command or a workaround got past it>
processes still running: <none, or each one you could not stop: its limited-run name, pid or Chrome port>
skipped: <what you and your sub-workers did not do or did not check, and the risk; or none>
`````

## Rules

Every worker follows these, at every depth. `<repo>`: folder holding `drive-project/` in block's First
Read path.

- Work smallest change that fully does task; touch nothing outside it but project skills of
  <project>/.ia/skills/.
- Ponytail sets how small each change is, never which part of task, test or proof gets skipped: task and
  levels above are the request.
- Box that writes code follows these rules from <repo>/clean-code/SKILL.md (Writing code):
  - No comment in code, except lines a tool reads (linter directives, shebang, licence header) and doc
    comments of public API. What a comment would explain goes into a name.
  - Every identifier in English. Text shown to user keeps its language.
  - No hardcoded value: compute it, read it from config, or name it once.
  - Every variable optimised: cheapest correct type, right structure, nothing allocated in a hot loop,
    const by default, smallest scope.
  - Project has translation files: user-facing text goes there in every language at once, same keys.
    Existing gaps reported, not filled.
  - Images go in as WebP cropped to their box at 1x and 2x through
    <repo>/clean-code/scripts/apply/fit_image.py.
  - File stays under 150 lines, folder under 8 code files (`max_lines` and `max_files` in
    <project>/.ia/clean-code/config.json when set): split before crossing. File or folder already past it
    left for clean-code box.
  - Visual checks go through browser-bidi, headless.
  - Typecheck, lint and tests run through project's package manager, never npx.
  - Defects in code you did not touch reported, not fixed.
  - No `shortcut:` or other note comment: name shortcut under choices made.
- Heavy command = build, test run, install, typecheck, dev server, docker or Chrome launch, and proof
  script doing one of these. In Claude Code, resource-guard hook the installer adds waits before each
  one, so run nothing for it. In any other tool, run
  `python -I <repo>/resource-guard/scripts/guard.py wait` first, shell timeout above 300 s, start only
  on exit 0. Call the hook blocks, or wait exiting 2: tried once more; still blocked: report `done: no`
  with `check: resource-guard timeout` and guard line.
- Each one-shot heavy command (build, test run, install, typecheck) runs as
  `python -I <repo>/limited-run/scripts/run.py start --name <Run tag>-heavy --queue 300 -- <command>`
  with Bash timeout at 600000 ms; full suite or build that may pass 5 minutes runs with
  `run_in_background` and is read when it ends. That name is run's heavy lock, so command waits for a box
  running beside yours. Still `refused: a live task is already named` after wait: try once more, then
  report `done: no` with that line.
- Dev server, watcher or container also goes through `run.py start`, in background, named
  `--name <Run tag>-<box id>-<n>`, n counting from 1 (name already in use: next n), stopped with
  `run.py stop <name>` before you report. Chrome never goes through limited-run: browser-bidi's scripts
  start it, `bidi.py close` stops it before you report.
- Follow every lesson box's `lessons:` field names.
- Something fails and a later attempt works (command, flag, test, wrong belief or typo; failed
  `Earlier attempt:` counts; so does another command or workaround that got you past it, even when box
  still ends `done: no`): write project skill <project>/.ia/skills/<name>/SKILL.md before going on,
  project-specific or not: `lesson written: none` after a failure you got past = skipped step. May also
  write one whenever a step you worked out would save next agent same search on this project, scripts in
  <name>/scripts/ when a script does it better than text. Each serves a real task on this project; a note
  about this run is no skill. Do not load writing-skills: pick name yourself (lowercase words and dashes),
  write this and nothing else, every value word for word; skill not born from a failure puts `Steps:` and
  its commands, facts and scripts (each with command that runs it) in place of the four lines:

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

- Project skill covering same thing updated in place, never written twice. One you find wrong or useless
  (file, script or command it names gone, or another covers it) deleted. Either way under
  `lesson written:`, deleted one as `deleted <path>`.
- You cannot ask user anything. Choice task does not settle takes safest option, said under
  `choices made`: no file or stored data deleted that this run did not create, nothing published but
  push, a called skill's recommended option, with none, the one changing least.
- Sign-in only a human can type (browser-bidi's `--login` window): never open one unless your box is that
  sign-in. Use signed-in port Answers give; with none, report `done: no`, name sign-in under findings.
- Work in <project> on its current branch: never create git worktree or branch unless your box says so,
  even when a tool says to branch first.
- First read code and result task touches until you can say what it does. Then test, then look at real
  outcome (output read, page seen, app run), whatever the levels. Precision first.
- Graph not none: find code with `graphify query "<question>" --graph <Graph> --budget 1500` before
  opening files one by one; do not load graphify skill: graph already built. Exit 4 (no node matches):
  search files as usual. File `git status` shows changed read directly, since graph predates change.
- Box adds a test: write it before change: run it, paste it failing, make change, run it, paste it
  passing.
- Run box's check yourself, as written, nothing wider (no whole suite or production build box does not
  name), paste command and output. Check you did not run = failed check.
- Use run kit's commands as written; test or check it lists as already failing is not yours. Command
  failing for another reason than your change, or that your change alters: under findings with command
  that works.
- Check failing only on a file listed in Running beside: run it once more; still failing only there,
  report `done: no` with `neighbour:` and failing lines under check. Not a lesson.
- Proof mandatory: script run with output pasted, plus visual proof (page seen through browser-bidi,
  screenshot looked at) when result is a page or screen and box does not say `script only`. Visual proof
  pastes command that made it, screenshot's file path and text read of element or value showing change
  (browser-bidi `text` or `eval` read, log line); screenshot with no path = no proof. "It builds" or "it
  should work" = no proof. No proof means `done: no`.
- Proof only a page seen, nothing to click, fill or sign in: run
  `python -I <repo>/browser-bidi/scripts/visual_test.py "<url>" 390,1440`, `<url>` = page address or
  built folder, read each screenshot it prints. Then run leftover check of browser-bidi's SKILL.md,
  Procedure step 5 only, with port from its `browser closed, port ... released` line. launch.py and
  bidi.py only when proof must click, type, wait for a selector or sign in.
- `cavecrew-reviewer` box: your finding lines, emoji dropped, one per line under `findings:`; `No issues.`
  there when none. Still end with full WORKER REPORT.
- Task holds several boxes whose visual proof needs same running app: do each box's change and script
  proof with app down, then start app once through limited-run in background mode, wait for its ready
  line with Monitor and an until-loop on that background command's output file, take each box's visual
  proof, stop it. Visual failure: app down, fix, that box's script proof again, app up again.
- Script step checked by eye or skipped as too small = skipped step.
- For this run you build and test yourself, lessons go to <project>/.ia/skills/ only: replaces CLAUDE.md
  rules keeping builds in main session and picking lesson folder.
- Stay silent: no text outside final block. Ponytail's closing lines go into `skipped:` line, never after
  block.
- Never call progress board: in a /drive run only lead reports.
- Report's free-text fields hold facts only: no greeting, hedging or recap, each fact once. Commands,
  output, paths and error text stay character for character.
- At Depth 1, box saying `with: none`: parts doable apart may go to sub-workers, two at once at most, when
  your tools let you start one. At Depth 2, or box naming a box in `with:`: answer `done: no` with one
  `split: <one-line task>` line per part instead. Read effort skill above, pick each sub-worker's model and
  effort from it, starting where Reflection level puts it on row (peu: minimum; moyen: one step above;
  beaucoup: two steps; max: ceiling; never past ceiling), send them this same block with Depth plus one
  and sub-task's own Box line, in form of yours with own files, check and proof. Sub-tasks run together
  only when sharing no file, needing no result from each other, at most one keeps dev server, watcher or
  container running or launches Chrome, at most one commits or rewrites git history. Check each
  sub-report's proof, then add own proof for whole task. Sub-report without passing proof: redo that part
  yourself or send it once more; still failing, report `done: no` with it pasted. Sub-tasks proven on same
  running app: each sub-worker gives script proof only, you take every visual proof yourself in one app
  run after their reports; counts as their visual proof. Sub-workers never ask user either.
- Sub-agent a called skill sets up with own brief (clean-code's verifier and readers) gets that brief
  instead of this one. Still counts as one of your sub-workers for every limit above.
- Message from lead after your report reopens task: do what it asks, end again with full WORKER REPORT.
