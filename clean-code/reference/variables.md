# Rule 16: every variable optimised

Applies to every field, local, parameter and constant written or touched. Correct first, then
cheapest; micro-gain off measured hot path never justifies harder code.

Types and structure: primitives over boxed wrappers (`Map<Integer, ...>` boxes every key: use
primitive-specialised collection or flat array); closed set of values = enum or named constants;
map lookup over linear scan, set over list `contains`, batched call over N+1, squared distance
against squared radius instead of `sqrt`.

Allocation and scope: no `new`, closure, iterator or boxing in loop that runs per tick, frame,
request or row; reuse scratch buffers kept as fields, hoist invariants, plain loop over stream chain
in hot path. Never reassigned = `const` or `final`, declared at first use in smallest block. State a
reflection or serialization layer rewrites (config holders, ORM fields) stays mutable. One source of
truth per fact.

Concurrency: state shared across threads needs atomic, lock, volatile, immutable snapshot or
channel. Synchronisation primitive that looks removable usually guards something: prove it unused
first.

Finding names variable, line and cheaper form ("`items` is a `List` used only for `contains` at
line 42, make it a `Set`"). "Could be optimised" is a guess.
