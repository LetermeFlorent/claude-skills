# Rule 16 in detail: every variable optimised

Applies to every field, local, parameter and constant you write or touch. Correct first, then
cheapest. A micro-gain off the measured hot path never justifies code that is harder to read.

## Type and representation

Use the cheapest correct type: primitives over boxed wrappers (`int`, not `Integer`; a value
struct, not a heap object) wherever the language draws that line.

Collections hide boxing. A `Map<Integer, ...>` boxes every key, so reach for a primitive-specialised
collection or a flat array: fastutil or Trove in Java, typed arrays in JS and TS, `array` or numpy
in Python, slices in Go, `Vec<T>` in Rust.

Size the value to its range. A number that lives in 1..15 is a small int, and a flag is a bit.
Booleans that always travel together pack into one bitmask.

A closed set of values is an enum or a set of named constants, never raw ints or string literals.
It costs nothing at runtime and removes a whole class of typo bugs.

Compare cheaply: squared distance against squared radius instead of a `sqrt`, lengths before
contents, the cheap predicate first in a chain.

## Algorithm and data structure

The right structure beats every micro-optimisation. A map lookup instead of a linear scan, set
membership instead of a list `contains`: fix the complexity first, tune constants after.

Pick the structure for the access pattern. Random key access wants a hash map, an ordered range a
tree or a sorted array, LIFO and FIFO a stack or a queue, membership a set. A container of the
wrong shape stays wrong in a hot path however much it is tuned.

Batch IO and never do N+1: group database, network and disk calls instead of one call per item in
a loop. Load lazily what may go unused, and cache an expensive call only when it is pure.

Exit early. Order conditions cheapest first, return as soon as the answer is known, break out of a
search on the first hit.

Never concatenate strings in a loop: use a builder or a join, pre-sized when the count is known.

## Allocation, usually the biggest cost

No `new`, no closure, no iterator and no boxing inside a loop that runs per tick, per frame, per
request or per row. Reuse scratch objects and buffers, index with a plain counted loop.

Scratch buffers live as fields, cleared and refilled, instead of being reallocated on each call.

Pipeline abstractions that allocate belong in cold setup code. Stream chains, LINQ,
comprehensions and `map` plus `filter` all build intermediates: in the hot path, write the loop.

Hoist invariants. A config value, the clock, `size()` or `len()` is read once into a local before
the loop.

## Scope and mutability

Anything never reassigned is `const` or `final` by default. It states intent and lets the
compiler fold constants and analyse escapes. State that a reflection or serialization layer
rewrites stays mutable (config holders, ORM fields): locking it breaks the framework.

A true constant lives once, as a static final or a module-level frozen value, never as one copy
per object.

Declare a local at first use, inside the block that needs it. A value used in one branch lives in
that branch: a smaller scope means a clearer lifetime and better register allocation.

One source of truth per fact, the rest derived from it. Caching a repeated read into a local
inside one method is fine; a second copy that can drift between calls is a defect.

## Concurrency

State shared across threads needs the right tool: an atomic, a lock, a volatile, an immutable
snapshot or a channel. A plain mutable field is none of these, and a synchronisation primitive
that looks removable usually guards something: prove it unused before taking it out.

State touched by a single thread needs no synchronisation, and a plain field is cheaper than an
atomic. Match the tool to the real sharing, in both directions.

## What a finding looks like

A rule 16 finding names the variable, the line, and the cheaper form: "`items` is a `List` used
only for `contains` in the loop at line 42, make it a `Set`". "Could be optimised" is a guess,
not a finding.
