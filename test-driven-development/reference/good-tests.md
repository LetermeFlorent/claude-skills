# Good tests

Read this before writing or changing a test, or adding a mock, a fixture or a test helper. A test
exists to catch one break, and two ideas carry everything below: a test can name the break it
catches, and it runs the real code. A test written first and watched failing against real code has
already passed both.

## Name the break

Before the body, say which change to the production code would make the test fail, and whether that
change would be a bug or a decision. A test earns its place by catching a wrong branch, a missing side
effect, a wrong argument, a boundary case or a broken contract.

The gate, before the body, works on what you can answer.

| You can name | Then |
|---|---|
| a bug that turns it red | write it |
| nothing | redesign it around something a caller can see |
| "the source text changed" | run the thing and assert what it does |
| only a deliberate choice: a constant, the wording of a message, a private shape | it is a change detector: test the behaviour that depends on the choice |

A change detector fires on every redesign and sleeps through bugs. Not `assertEqual(MAX_RETRIES, 5)`,
but "a failing call is tried five times and the sixth attempt never happens".

## Expected values come from the rule

Work out every expected value by hand, from a rule someone stated: the task, an issue, the README, the
function's documented contract. Literals and hand-checked fixtures; a table of cases with literal
expected values is the shape to reach for. A value computed by the code under test, or by its helpers,
agrees with that code whatever it does. Both sides of this one come from the same builder:

```python
self.assertEqual(build_query(tag="urgent"), build_query(tag="urgent"))
```

This one was worked out by hand:

```python
self.assertEqual(build_query(tag="urgent"), 'tag:"urgent"')
```

Never run the code and paste its output as the expected value: that records what it does, not what it
should do. Never invent a rule the task and the code do not have. A rounding mode, a limit or an error
type nobody stated is a question for the user, asked with `AskUserQuestion`, not a guess frozen into a
test.

When a test written from the rule fails on code that already exists, either the code or the rule is
wrong. The expected value never moves toward the code to make the test pass.

## Behaviour, not text

A test that checks a script, a skill or a config file holds a given line proves the file is the file.
Run the script on controlled input and assert its output, its side effects or its exit code. A
document that instructs an agent is tested through the agent's behaviour (the `writing-skills`
skill); prose for people gets no test.

## Your code, not the framework

Test the contract at your own boundary: the route you register, the query you build, the payload you
send. Whether the router calls a registered handler is the framework's test. When the framework did
surprise you, one narrow test names the assumption. Inside your code, a constructor, a getter, a
constant or a plain forward earns a test only when it validates, normalizes, defaults, derives or has
a side effect. Otherwise, test the first result a caller sees.

## Mock the boundary, keep the rest real

A unit test never reaches the network, a real API, a mail server or a payment service, a staging host
included. Mock that boundary at the lowest level that keeps the test fast and offline, and keep
everything above it real, the function under test first of all. The clock, randomness, files outside
a temporary folder and slow external processes are boundaries too.

```python
with mock.patch("shipping.client.fetch_json", return_value={"price": 4.9, "currency": "EUR"}):
    self.assertEqual(quote(parcel_of(2)), 9.8)
```

Before replacing a method, list what it does besides returning a value: a write that the test reads
later, a cache, a registration. Mock below those effects, never above them. In doubt, run the test
once against the real method and watch what it needs.

The mock earns no assertion of its own. A test that only checks the mock was called passes as long as
the mock is there and says nothing about your code. Assert on the result. Arguments, call counts and
order are asserted when they are the contract (the URL hit, the amount charged), and then next to an
assertion on the result. A fake that accepts anything checks nothing: success, an error and a
malformed answer each get their own fixture, so the wrong branch cannot satisfy the test.

A mocked response mirrors the real structure completely, every documented field and not only the ones
the test reads. A partial one passes while the real integration breaks on the field it left out.

When the mock setup is longer than the test, misses methods the real object has, or breaks the tests
each time it changes, switch to a test on real components.

## Tests are code

Cleanup that only tests need lives in test helpers, never as a `reset()` or `destroy()` on a
production class. A method that only test files call moves out of the production code.

Tests follow the `clean-code` skill like any other code: no comment, English names, a file under 150
lines, split by behaviour before it crosses. Expected values are literals on purpose; a setup value
used in several tests gets one name.

Keep the project's layout and naming: its test folder, its file names, its test names, its runner,
its assertion style. Read two neighbouring tests before writing one. A project that writes
`test_total_empty` gets no `test_should_return_zero_when_cart_is_empty`, and a project on
`unittest.TestCase` gets no pytest fixture.

## The mutation check

Before finishing, break the new code in your head, one realistic break at a time, and point at the
test that fails for each: a wrong constant or argument, the wrong branch, a missing state change or
side effect, an empty or default return, missing validation of zero, empty, missing, unauthorized or
malformed input. A break no test catches marks behaviour nobody protects, or a test that checks
nothing.

For code that existed before its tests, make the break for real: change the covered line, run the
test, read the red, put the line back with an edit (never `git checkout`, `git restore` or
`git stash`), and run it green.

## Warning signs

Each of these means the test gets rewritten or deleted.

| Sign | What is wrong |
|---|---|
| setup and assertion share one object | equal by construction |
| it can only fail by a crash or a missing selector | no behaviour is checked |
| it fails on every deliberate change and never on a bug | change detector |
| expected values hidden in loops, builders or helpers | a mirror of the code |
| it greps source text, or checks a removed symbol stays removed | tests the file, not the behaviour |
| it would still pass with only the framework left | not your code |
| written for coverage, no outcome checked | upkeep that catches nothing |
| asserts on a `*-mock` test id, or fails when the mock goes | tests the mock |
| a method only test files call | test code in production |
| mock setup over half the test, or a mock added "to be safe" | the code is too coupled, or the mock is useless |
| names in a style the project does not use | not the project's tests |
| it calls a real host, even a staging one | slow, flaky, and not a unit test |
