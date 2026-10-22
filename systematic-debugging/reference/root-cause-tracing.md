# Root cause tracing

## Overview

A bug often surfaces far from where it starts: a `git init` that runs in the wrong folder, a file
written to the wrong place, a database opened on the wrong path. Fixing the line that fails treats
the symptom. Walk the calls backward until you reach the first place the value went wrong, and fix
it there.

## When to trace

Trace when the error happens deep in the run rather than at the entry point, when the stack trace
is long, when nobody knows where a bad value came from, or when you need to know which test or
caller sets it off. When the trail goes cold (a value from outside the process, a callback whose
caller is gone), fix as close as you can to where that value enters, and add the checks from
`defense-in-depth.md`.

## The steps

Each step asks one question and answers it with something you saw, never something you assumed.
The example comes from a real session, in a TypeScript project.

1. Symptom, the exact error: `git init failed in ~/project/packages/core`.
2. Immediate cause, the line that does it: `execFileAsync('git', ['init'], { cwd: projectDir })`.
3. Callers, walked up the stack: `WorktreeManager.createSessionWorktree`, called by
   `Session.initializeWorkspace`, called by `Session.create`, called by a test through
   `Project.create`.
4. Values, at each level: `projectDir` was `''`, and an empty `cwd` means the current folder, which
   was the source tree.
5. Origin, where the bad value was born: the test read `context.tempDir` when the module loaded,
   before `beforeEach` set it, and `setupCoreTest()` starts with `{ tempDir: '' }`.

The fix went to step 5: `tempDir` became a getter that throws when read before the setup ran. The
layers in between got their own checks afterwards, and the `.git` folders stopped appearing in the
source tree.

## When the stack is not enough

Instrument the dangerous operation just before it runs: what it receives, where it runs, who called
it.

```python
import os
import sys
import traceback


def git_init(directory):
    print(f"DEBUG git_init directory={directory!r} cwd={os.getcwd()!r}", file=sys.stderr)
    traceback.print_stack(file=sys.stderr)
    ...
```

```typescript
console.error('DEBUG git init', { directory, cwd: process.cwd(), stack: new Error().stack });
```

Write to stderr: test runners often swallow the project's logger, rarely stderr. Log before the
operation, not after it fails, and include the folder, the working directory and the environment
variables involved. Run once with the output going to `$SCRATCH`, then filter it:
`npm test 2>&1 | grep 'DEBUG git init' > "$SCRATCH/trace.log"`. Read the stacks for test file
names, the line that triggers the call, and what repeats (the same test, the same argument).

These lines are temporary. They come out by an edit before the fix is committed.

## Finding the test that pollutes

When the bad state appears during the suite and nobody knows which test causes it,
`scripts/find_polluter.py` finds it (see "Test pollution" in SKILL.md). Without the script, the
bisection by hand goes like this: run the victim alone, it must pass; run every other file then the
victim, it must fail; then keep whichever half still makes the victim fail, until one file is left.
When neither half fails on its own, two files are needed together: report both halves.

## The principle

Never fix only where the error appears. Go up one level at a time until the level above holds good
data: the boundary you just crossed is the source.
