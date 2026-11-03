# Rule 16: every variable optimised

Applies to every field, local, parameter and constant written or touched. Correct first, then
cheapest; a micro-gain off the measured hot path never justifies harder code.

Types and structure: primitives over boxed wrappers (a `Map<Integer, ...>` boxes every key: use a
primitive-specialised collection or flat array); a closed set of values is an enum or named
constants; a map lookup over a linear scan, a set over a list `contains`, a batched call over N+1,
squared distance against squared radius instead of `sqrt`.

Allocation and scope: no `new`, closure, iterator or boxing in a loop that runs per tick, frame,
request or row; reuse scratch buffers kept as fields, hoist invariants, prefer a plain loop to a
stream chain in the hot path. Anything never reassigned is `const` or `final`, declared at first use
in the smallest block. State that a reflection or serialization layer rewrites (config holders, ORM
fields) stays mutable. One source of truth per fact.

Concurrency: state shared across threads needs an atomic, lock, volatile, immutable snapshot or
channel. A synchronisation primitive that looks removable usually guards something: prove it unused
first.

A finding names the variable, the line and the cheaper form ("`items` is a `List` used only for
`contains` at line 42, make it a `Set`"). "Could be optimised" is a guess.
