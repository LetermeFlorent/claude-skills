# Rule 18: as few hardcoded values as possible

In order: compute the value from what it depends on (`PADDING + ICON_SIZE`, `ceil(total / perPage)`,
the length of the list itself); else read it from configuration when it changes between machines,
environments or users (URLs, hosts, ports, paths, accounts, limits), with a key and a sensible
default but never the production value, and no default for a secret; else name it once at module
level (protocol number, unit conversion, format string).

`checks/files/hardcoded.py` flags per file: numbers other than 0, 1, -1 outside a named constant,
enum or import; comparisons with a literal (`status === "paid"`); environment values (URLs,
`localhost`, absolute paths, emails) unless the line reads the environment; string literals of 3+
characters repeated in the file. It skips CSS, HTML, SQL, shell, component templates and test files
(code written for a test still names what it shares between cases).

## Not a finding

`0`, `1`, `-1`, an empty string, `true`, `false`; an index into a fixed tuple; the value inside its
own name (`HTTP_OK = 200`); expected data in a test; a format required by an outside API.
