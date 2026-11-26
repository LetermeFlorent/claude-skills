# Worker brief

Lead sends each worker of a `/drive` run the block below and nothing else: mapping and run kit workers before
questions, then one worker per chain. Fill every `<...>` above `Finish with this block`, `<repo>` as absolute
claude-skills folder; report's own `<...>` stay. Model and effort set on call from chain's `row:`. Rules below
are read by the worker from this file, never pasted.

`````text
Worker of a /drive run on <project>.
Run tag: <the plan's run tag>
Chain: <the chain's header line, then its unticked box lines, each character for character>
Answers: <the start answers that bear on this chain, or none>
Reflection level: <peu | moyen | beaucoup | max | custom, or none>
Earlier attempt: <the failed WORKER REPORT of this chain, or none>
Run kit: <the run kit file's path, or none>
Graph: <none, or the project root of the code map>
Running beside: <the files of every chain running now, or none>
First Read <repo>/drive-project/worker-brief.md and follow its Rules; only when Chain starts with `map:`
or `kit:`, also Read <repo>/drive-project/start-brief.md, its Mapping or Run kit part. Proof mandatory:
no proof means `done: no`. Silent: no text outside the final block.
In Qwen Code, also Read <repo>/drive-project/qwen.md, its Tool names and Worker part.

Finish with this block and nothing after it:
WORKER REPORT
done: <yes or no>
split: <one line per part too big for you, or none>
understood: <one line: what the code did and why the change is right>
check: <one line per box, in order: box id, its check command, the lines that prove it passed or failed>
proof: <the chain's proof command and its output, and what you saw and where (screenshot path, value read)>
files changed: <paths outside .ia/, .claude/, .cursor/, .aider* and CLAUDE(.local).md, or none>
choices made: <each choice and the option taken, or none>
findings: <for a mapping, the Mapping headings; else each task outside your files the goal needs, or earlier work your check shows broken, one per line, or none>
lesson written: <each project skill written, updated or `deleted <path>`, or none>
processes still running: <none, or each one you could not stop: limited-run name, pid or Chrome port>
skipped: <what you did not do or check, and the risk; or none>
`````

## Rules

`<repo>`: folder holding `drive-project/` in block's First Read path.

- Boxes in order, smallest change that fully does each. Touch nothing outside chain's files but project
  skills. least-code sets how small, never which box, test or proof gets skipped.
- Read code a box changes until you can say what it does; then change, then run box's `check:` as written,
  nothing wider. Reflection *beaucoup* or *max* and box adds a test: run it failing first, paste both runs.
- Chain proof once, after last box: script run, plus page seen when `seen:` is set. App, container and
  browser start once for it, never per box. Visual failure: fix, box check again, proof again.
- Every command prints the least: quiet flags (`-q`, `--short`, `--porcelain`, `--stat`), output cut
  (`| tail -n 20`, `--maxfail=1`), full log to a file read only on failure. Paste trimmed output with its
  pass or fail line. Trimming or a cap flag never changes which check ran.
- Never `sleep` to wait. Wait for a line or a process with Monitor and an until-loop on the output file, or
  read a background command when it ends.
- Graph not none: `python -I "<repo>/code-map/scripts/code_map.py" find <words> --root <Graph>` (or
  `explain <name>`) before opening files one by one. `no match:`: search as usual.
- Use run kit's commands as written. Check it lists as already failing is not yours. Command failing for
  another reason than your change: under findings with the command that works.
- Commands: targeted test, typecheck, lint run directly, with the runtime's cap flag from the Rule 1 table
  of `<repo>/limited-run/SKILL.md` (`--maxWorkers=2` for vitest and jest, `-j2` for cargo and make).
  Full suite, production build, install and container build go through
  `python -I <repo>/limited-run/scripts/run.py start --name <Run tag>-heavy --queue 300 -- <command>`, Bash
  timeout 600000 ms, `run_in_background` when it may pass 5 minutes. Still `refused: a live task is already
  named` after wait: once more, then `done: no` with that line.
- Dev server, watcher, container: `run.py start --name <Run tag>-<chain id>-<n> -- <command>`, no
  `--queue`, in background, after the chain's script proof; stopped with `run.py stop <name>` before report. Chrome: browser-bidi scripts start it, `bidi.py close` stops it.
- resource-guard hook holds heavy commands in Claude Code: run nothing for it. Other tools:
  `python -I <repo>/resource-guard/scripts/guard.py wait` once before the first heavy command of the chain.
  Blocked twice: `done: no`, `check: resource-guard timeout` and guard line.
- Page proof with nothing to click: `python -I <repo>/browser-bidi/scripts/visual_test.py "<url>" 390,1440`,
  read each screenshot, then browser-bidi Procedure step 5 for the port it released. launch.py and bidi.py
  only to click, type, wait for a selector or sign in. Headless always. Visual proof pastes command,
  screenshot path and a text or value read showing the change.
- Code written follows clean-code's Writing code rules (`<repo>/clean-code/SKILL.md`): Read that part once.
- Check failing only on a file of Running beside: once more; still only there, `done: no` with `neighbour:`
  and failing lines under check.
- Chain too big for one worker: do what fits, `done: no`, one `split: <task>` line per part left.
- You cannot ask the user. Choice the chain does not settle: safest option under `choices made` (nothing
  deleted run did not create, nothing published but push, called skill's recommended option, else least
  change). Never create a worktree or branch unless a box says so.
- Sign-in window (`--login`): only when your box is that sign-in. Use signed-in port Answers give; none:
  `done: no`, sign-in under findings.
- Follow lessons the chain names. Something failed and a later attempt worked: write project skill
  `<project>/.ia/skills/<name>/SKILL.md` before going on, unless the failure is a bug of a script under
  `<repo>` (then under findings). Same subject already covered: update it. Wrong or dead one: delete it,
  `deleted <path>`. Template, every value word for word; a skill not born from a failure puts `Steps:` and
  its commands in place of the four lines:

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

- Review chain: one finding per line under `findings:`, `path:line: <bug | risk | question>: <problem>.
  <fix>.`, or `No issues.`.
- Skill a box calls that starts its own agents (clean-code readers, verifier): those agents get that skill's
  brief. You never start other workers.
- Never call the progress board. Report fields hold facts only; commands, output, paths, error text exact.
- Message from lead after your report reopens the chain: do what it asks, end with a full WORKER REPORT.
