# Rule 18 in detail: as few hardcoded values as possible

A value written in the code is a decision frozen where nobody looks for it. The order is fixed.

Compute it first, from what it depends on: a width that is a padding plus an icon size is
`PADDING + ICON_SIZE`, a timeout that must exceed a retry loop is `retries * delay` plus a margin, a
page count is `ceil(total / perPage)`, the length of a list comes from the list.

Read it from configuration next when it changes between machines, environments or users: URLs,
hosts, ports, paths, accounts, switches, limits a user tunes. The code holds the key and a sensible
default, never the production value, and a secret never has a default.

Name it last. What is left is a true constant (a protocol number, a unit conversion, a format
string): one name, once, at module level, and every use goes through it.

## What the script flags

`checks/files/hardcoded.py` reports, per file:

- numbers other than 0, 1 and -1 outside a named constant, an enum or an import;
- comparisons with a literal (`status === "paid"`, `count > 50`);
- environment values: URLs, `localhost`, absolute paths, emails, unless the line reads the
  environment;
- string literals of three characters or more repeated in the same file.

It skips CSS, HTML, SQL, shell and component templates, where literals are the medium, and test
files, whose literals are the expected values. Code written for a test still names what it shares
between cases.

## Not a finding

`0`, `1`, `-1`, an empty string, `true` and `false`; an index into a fixed tuple; a value that is
its own name (`HTTP_OK = 200` is the name, the 200 inside it is fine); a literal inside a test's
expected data; a format required by an outside API. The verifier refutes those.
