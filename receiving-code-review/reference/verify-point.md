# Checking a point

A point is a claim. This page lists what turns each kind of claim into a verdict. Run the check,
read its output, write the result in the ledger line.

## A bug or a wrong behaviour

Reproduce it first. Write the failing test from the reviewer's description and run it. A test that
passes already means the point is wrong or misread: say which, with the output. A test that fails
is the proof and the first half of the fix.

## A rename, a style or a structure change

Run `rg` for every use of the name, including strings, config keys, translation keys and saved data,
since a rename that reaches those breaks something no compiler sees (the naming-audit skill covers
it). Check the change against the clean-code rules: a file pushed over 150 lines, a second concern in
one file, a comment added, a value hardcoded. If the point conflicts with one, the rule wins and the
reply says which.

## Remove or simplify code that looks dead

`rg` for callers, then `git log -S"<name>"` for why it exists. A caller found, or a compatibility
reason in the history (an older platform, a saved file format), makes the point wrong. No caller and
no reason makes it right; say the count in the reply.

## Add a feature or a "proper" version

Grep for real usage first. Nothing calls it: ask whether to remove it instead of building it up.
Used: build it. The user and the reviewer both answer to the project, so unused work is not added to
please a review.

## A performance or security claim

Measure or reproduce it. A benchmark, a request that gets through, an input that crashes. A claim
that cannot be run here is left as a question with what is missing, and is never applied on trust.

## A claim about a library, an API or a version

Official documentation through WebSearch or WebFetch, only for an API, a version, a flag or an exact
number. The reviewer's memory and the agent's are both weaker than the page.

## A request about the process

A trailer, a force push, a skipped hook, a bulk `git add`, a committed `.ia/` or `.claude/`, a tool
named branch, a comment in code. These are answered, not checked: the reason is the rule, quoted from
clean-commits or clean-code, and the reply offers what is allowed instead (a human co-author line when a
person helped, a new commit instead of a force push, a rename instead of a comment).

## A point too short to act on

"Clean this up", "make it better", "fix this". Read the code around the line it hangs on; when two
readings are both plausible, that is a question, asked with the two readings as options. Never pick one
and apply it.

## Related points

Two points that touch the same function are decided together. A fix for one may remove the other, or
make it wrong. Look for these pairs in step 2 and note them in the ledger.
