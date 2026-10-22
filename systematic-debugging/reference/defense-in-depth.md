# Defense in depth

## Overview

Once the source is fixed, one check at one place feels enough. Another code path, a refactor or a
mock can still go around it. When bad data crossed several layers on its way to the failure, give
each layer it crossed a check of its own, so the bug cannot come back by another road.

## The four layers

Each layer catches cases the others let through.

| Layer | Its job | In the empty `projectDir` case |
|---|---|---|
| Entry | refuse plainly invalid input at the boundary of the API | `create_project` rejects an empty, missing or non-folder directory |
| Business logic | check the data makes sense for this operation | `initialize_workspace` requires a project folder |
| Environment guard | refuse a dangerous operation where it must never run | during tests, `git_init` refuses any folder outside the temp folder |
| Diagnostics | leave a trace for the next investigation | the project's logger records the folder and the caller before `git init` |

The first and third layers, in Python:

```python
TEST_MODE_VARIABLE = "APP_TEST_MODE"
TEMP_ROOT = Path(tempfile.gettempdir()).resolve()


def create_project(name, working_directory):
    if not working_directory or not working_directory.strip():
        raise ValueError("working_directory is empty")
    if not Path(working_directory).is_dir():
        raise ValueError(f"working_directory is not a folder: {working_directory}")
    ...


def git_init(directory):
    inside_temp = Path(directory).resolve().is_relative_to(TEMP_ROOT)
    if os.environ.get(TEST_MODE_VARIABLE) and not inside_temp:
        raise RuntimeError(f"refusing git init outside {TEMP_ROOT} during tests: {directory}")
    ...
```

The diagnostics layer goes through the project's own logger, at debug level, and only when the
project already logs that kind of event. A stray `print` left from the investigation is not a
layer: it comes out. No comment explains a check; its error message does.

## Applying it

Start from the trace that found the source.

1. Follow the data from where it is born to where it failed (`root-cause-tracing.md`).
2. List every point it passes through.
3. Add the check that fits each point. A check on a path no data takes is dead code: add checks
   where the bad data travelled, not everywhere.
4. Test each check: go around the first layer in a test and watch the second one catch it.

In the session this comes from, each of the four layers caught a case the others missed: code paths
that skipped the entry check, mocks that skipped the business check, a platform edge case only the
guard stopped, and a misuse found from the logs.
