# Shape of a plan

The plan is a markdown file in `<repo>/.ia/plans/`, read by the user and by `scripts/plan_lint.py`. Prose follows
the language of the spec (French when the spec is French); labels, headings, paths, identifiers and code stay
English because the linter reads them. The linter refuses a plan that drops a label, a heading or a step shape
described here.

## Header

Four label lines open the plan, then two sections. Global constraints copies the spec's project-wide limits
verbatim: version floors, dependency limits, naming and copy rules, platform. Every task inherits them. Review
focus lists the five inputs or failures the spec implies and no task's tests reach, most likely first; each line
also gets its test, added to the task that owns the code.

`````markdown
# <Feature> plan

Goal: <one sentence>
Architecture: <two or three sentences>
Stack: <languages, libraries, test runner>
Spec: <path of the spec in .ia/specs/>

## Global constraints

- <exact value copied from the spec>
- files under 150 lines, one concern per file, no comment, English names, no hardcoded value

## Review focus

- <input or condition>: <behaviour a reasonable person expects>
`````

## Task

A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate. Setup,
configuration and documentation fold into the task whose deliverable needs them. Split only where a reviewer
could reject one task and approve its neighbour.

`````markdown
### Task <n>: <component, in words>

Files:
- Create: `exact/path/file.ext` (about 60 lines)
- Modify: `exact/path/existing.ext:123-145`
- Delete: `exact/path/old.ext`
- Test: `exact/path/test_file.ext`

Consumes: <what earlier tasks give this one, exact signatures>
Produces: <names, parameter and return types that later tasks rely on>

- [ ] Step 1: Write the failing test

<complete test code in a fenced block>

- [ ] Step 2: Run the test and watch it fail

Run: `<one targeted command, one worker>`
Expected: FAIL with "<the message>"

- [ ] Step 3: Write the smallest code that passes

<complete code in a fenced block>

- [ ] Step 4: Run the test and watch it pass

Run: `<same command>`
Expected: PASS

- [ ] Step 5: Commit through clean-commits

Paths: `exact/path/file.ext`, `exact/path/existing.ext`, `exact/path/old.ext`, `exact/path/test_file.ext`
Intent: <one sentence in the repository's commit language>
`````

Rules the linter applies to this shape:

- Every `Create`, `Modify`, `Delete` and `Test` path of the task appears in `Paths:` of the commit step, and
  nothing else does. Line ranges after a colon are ignored on both sides.
- A size note on a `Create` line (`about N lines`) above 150 is refused: split the file in the plan.
- A task with nothing to test (documentation, configuration, a file move) writes `No test: <reason>` on a line
  before `Files:` and drops steps 1 to 4 for a single step that runs the check that proves the change, still
  followed by the commit step.
- The last step of every task is the commit.

## What is never in a plan

A plan that holds one of these is refused, because the executor would have to invent the missing part.

- TBD, TODO, FIXME, "implement later", "fill in details".
- "Add appropriate error handling", "handle edge cases", "write tests for the above" with no test code.
- "Similar to Task N": repeat the code, the executor may read tasks out of order.
- A step that says what to do without showing how, where code is involved.
- A name used in a later task that no earlier task defines, or spelled differently from where it was defined.
- A command that stages a whole tree, pushes, pulls, fetches, skips hooks or rewrites a commit.
