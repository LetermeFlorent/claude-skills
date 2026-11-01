# Rule 16 in detail: every variable optimised

Applies to every field, local, parameter and constant you write or touch. Correct first, then
cheapest. A micro-gain off the measured hot path never justifies code that is harder to read.

## Type and structure

Use the cheapest correct type: primitives over boxed wrappers wherever the language draws that
line. Collections hide boxing: a `Map<Integer, ...>` boxes every key, so reach for a
primitive-specialised collection or a flat array (fastutil or Trove in Java, typed arrays in JS and
TS, `array` or numpy in Python). A closed set of values is an enum or named constants, never raw ints
or string literals.

The right structure beats every micro-optimisation: a map lookup instead of a linear scan, set
membership instead of a list `contains`, a batched call instead of one per item in a loop (N+1).
Compare cheaply: squared distance against squared radius instead of a `sqrt`.

## Allocation and scope

No `new`, no closure, no iterator and no boxing inside a loop that runs per tick, per frame, per
request or per row: reuse scratch buffers kept as fields, hoist invariants (`size()`, the clock, a
config value) into a local, and write the loop instead of a stream chain in the hot path.

Anything never reassigned is `const` or `final`, declared at first use in the smallest block. State
that a reflection or serialization layer rewrites stays mutable (config holders, ORM fields):
locking it breaks the framework. One source of truth per fact: a second copy that can drift between
calls is a defect.

## Concurrency

State shared across threads needs an atomic, a lock, a volatile, an immutable snapshot or a channel;
a plain mutable field is none of these. A synchronisation primitive that looks removable usually
guards something: prove it unused before taking it out. State touched by a single thread needs none.

## What a finding looks like

A rule 16 finding names the variable, the line and the cheaper form: "`items` is a `List` used only
for `contains` in the loop at line 42, make it a `Set`". "Could be optimised" is a guess, not a
finding.
