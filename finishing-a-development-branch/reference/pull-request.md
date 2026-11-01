# Pull request

Read this when the answer is a push with a pull request.

## Push

From the branch's folder (the worktree or the repository), after the tests and the attribution check:

`python -I "<clean-commits>/scripts/push.py"`

It refuses a detached HEAD, an operation in progress and an unpushed commit carrying an attribution. It
never forces: on `rejected` the remote has commits the branch lacks (rule 4 of the skill). No remote
means the commits stay local, and the skill says so. For a detached HEAD, create the branch first (`git switch -c <name>`), with a name the user gave or confirmed that follows the
repository's convention and never starts with `claude/`, `codex/`, `copilot/`, `cursor/` or `devin/`.

## Body

The draft lives in `<main repository>/.ia/finir/pr-<branch>.md`, which stays out of git. Its form comes from
the repository, in this order.

1. The template named on the `pull request template` line of `state.py`. Keep its headings as they are,
   fill each one in prose, leave a section empty only when it does not apply. Tick a checkbox only for
   something done and checked in this run.
2. No template: two to four short paragraphs in the repository's language. What the change does and why,
   how it was verified (the test command and its result from this run), and what a reviewer should look at
   first when something is delicate.

The body never holds the stock "Summary / Changes / Test plan" outline, a row of checkboxes nobody ticked,
bold lead-ins, a closing recap, or any line or link naming an AI tool. It follows anti-empreinte: straight
quotes, no em dash, no emoji, headings in sentence case, mixed sentence lengths.

Check it before use:

`python -I "<anti-empreinte>/scripts/scan.py" "<draft>" --no-git`

Fix every row it reports.

## Title

One line under 72 characters, in the mood of the repository's commit subjects (look at `git log`). The
`type(scope):` form only when the history uses it.

## Opening it

The account is the owner in the remote URL; `state.py` prints it on the `remote` line.

```
gh pr create --base <base> --head <branch> --title "<title>" --body-file "<draft>"
```

Run it as rule 4 of the skill says. Read the URL gh prints and give it in the report. If the call fails, print its error and
keep the draft; do not retry with a bare `gh`.

A remote that is not on GitHub (a local bare repository, an ssh server) cannot open a pull request from
here: the push is done, the draft stays in `.ia/finir/`, and the report says where.
