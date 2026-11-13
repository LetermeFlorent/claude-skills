# Rule 18: as few hardcoded values as possible

In order: compute value from what it depends on (`PADDING + ICON_SIZE`, `ceil(total / perPage)`,
length of list itself); else read it from configuration when it changes between machines,
environments or users (URLs, hosts, ports, paths, accounts, limits), with key and sensible default
but never production value, no default for secret; else name it once at module level (protocol
number, unit conversion, format string).

`checks/files/hardcoded.py` flags per file: numbers other than 0, 1, -1 outside named constant,
enum or import; comparisons with literal (`status === "paid"`); environment values (URLs,
`localhost`, absolute paths, emails) unless line reads environment; string literals of 3+
characters repeated in file, secret-looking ones masked. Skips CSS, HTML, SQL, shell, component
templates and test files (code written for a test still names what it shares between cases).

## Not a finding

`0`, `1`, `-1`, empty string, `true`, `false`; index into fixed tuple; value inside its own name
(`HTTP_OK = 200`); expected data in test; format required by outside API.
