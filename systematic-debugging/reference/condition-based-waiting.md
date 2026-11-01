# Condition-based waiting

A test that sleeps for a fixed time guesses how long something takes: it passes on a fast machine and
fails under load, in CI, or when the suite runs in parallel. Wait for the condition you care about, with
a deadline.

## In test code

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

Three mistakes come back often, whatever the language. Polling every millisecond burns CPU that other
sessions on this machine share; 10 ms is enough. A loop with no deadline hangs the suite when the
condition never holds, so always a deadline and an error that names what was awaited. Reading the state
once before the loop waits on a stale copy: call the getter inside the loop.

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
finished, with the bounded loop of `SKILL.md`, adapted to the log:

```
for i in $(seq 60); do grep -qE 'Listening on|Error|EADDRINUSE' "$SCRATCH/server.log" && break; sleep 2; done
```

It reads what the log already holds, so a line written before it started still counts; `grep` fails
quietly while the log does not exist yet, and the loop keeps waiting. A process with no log of its own
gets one: start it in a background Bash call with its output going to `$SCRATCH/<name>.log`, then wait on
that file. Never a series of calls that wake every few seconds to tail a log, since each wake-up costs a
whole turn. A server started for the repro is stopped before the end of the task.
