# Condition-based waiting

## Overview

A test that sleeps for a fixed time is guessing how long something takes. It passes on a fast
machine and fails under load, in CI, or when the suite runs in parallel. Wait for the condition you
care about, with a deadline. The same holds outside the code: a build or a server is awaited
through the line it writes, not through a pause.

## In test code

The signs are a `sleep`, `setTimeout` or `time.sleep` in a test, a test that fails now and then or
only under load, and timeouts that appear when tests run in parallel.

```python
POLL_INTERVAL_S = 0.01
DEFAULT_TIMEOUT_S = 5.0


def wait_for(condition, description, timeout=DEFAULT_TIMEOUT_S):
    deadline = time.monotonic() + timeout
    while True:
        result = condition()
        if result:
            return result
        if time.monotonic() > deadline:
            raise TimeoutError(f"no {description} after {timeout} s")
        time.sleep(POLL_INTERVAL_S)
```

```typescript
const POLL_INTERVAL_MS = 10;
const DEFAULT_TIMEOUT_MS = 5000;

export async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    const result = condition();
    if (result) return result;
    if (Date.now() > deadline) throw new Error(`No ${description} after ${timeoutMs} ms`);
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }
}
```

The condition changes with what you wait for.

| Waiting for | Condition |
|---|---|
| an event | `wait_for(lambda: find_event(events, "DONE"), "DONE event")` |
| a state | `wait_for(lambda: machine.state == READY, "ready state")` |
| a count | `wait_for(lambda: len(items) >= expected, f"{expected} items")` |
| a file | `wait_for(path.exists, f"file {path}")` |

Three mistakes come back often. Polling every millisecond burns CPU that other sessions on this machine
share; 10 ms is enough. A loop with no deadline hangs the suite when the condition never holds, so
always a deadline and an error that names what was awaited. Reading the state once before the loop
waits on a stale copy: call the getter inside the loop.

## When a fixed delay is right

A delay belongs in a test when the behaviour under test is itself timed: a debounce, a throttle, a
tick. Wait for the trigger first, then for a duration computed from the known timing. The reason
lives in the constant's name, not in a comment.

```python
wait_for(lambda: find_event(events, "TOOL_STARTED"), "TOOL_STARTED event")
time.sleep(TICKS_TO_OBSERVE * TICK_INTERVAL_S)
```

## Outside the code: logs and processes

A build, a server starting, a deploy or a long test run is awaited through the line that says it
finished, with a bounded loop.

```
for i in $(seq 120); do grep -qE '<done line>|<failure line>' <log> && break; sleep 2; done
for i in $(seq 60); do grep -qE 'Listening on|Error|EADDRINUSE' "$SCRATCH/server.log" && break; sleep 2; done
```

It returns as soon as either line appears and gives up after the last round (240 s and 120 s here). Read the
last lines of the log to see which pattern came first. It reads what the log already holds, so a line
written before it started still counts; `grep` fails quietly while the log does not exist yet, and the loop
keeps waiting.

A process with no log of its own gets one: start it in a background Bash call with its output going
to `$SCRATCH/<name>.log`, then wait on that file. With no line to wait for at all, one `sleep` of
30 s at most, or `run_in_background` and its notification when the command ends. Never a series of calls that
wake every few seconds to tail a log: each wake-up costs a whole turn. A server started for the
repro is stopped before the end of the task.
