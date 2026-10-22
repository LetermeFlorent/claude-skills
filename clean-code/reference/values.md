# Rule 18 in detail: as few hardcoded values as possible

A value written in the code is a decision frozen where nobody looks for it. Compute it from what it
depends on, read it from config, or name it once. This holds for every line written, in an audit
or in any other task.

## Compute first

Before naming a number, ask what it is made of. A width that is the sum of a padding and an icon
size is `PADDING + ICON_SIZE`. A timeout that must exceed a retry loop is `retries * delay` plus a
margin. A page count is `ceil(total / perPage)`. A column count comes from the container width. The
length of a list comes from the list. Then the value follows when its inputs change, and nobody
updates two places.

## Then read it from where it belongs

Anything that changes between machines, environments or users comes from configuration: URLs,
hosts, ports, paths, account names, emails, feature switches, limits a user tunes. The code holds
the key and a sensible default, never the production value. A secret never has a default.

## Only then name it

What is left is a true constant: a protocol number, a unit conversion, a format string, a magic
header. It gets one name, once, at module level, and every use goes through that name. A literal
repeated in three places is three chances to drift.

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
