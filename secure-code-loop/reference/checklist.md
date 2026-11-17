# Security checklist

Read when writing new code in scope, or when `scan.py` prints `not covered: code` and scope files get reviewed by
hand. Each flaw seen by hand goes into `advisories.txt` as `open <level> review-<n> <file> : <flaw>`. Scanners
catch only part of this list; SonarQube Community Build has no taint analysis, so injections through several
functions slip past it.

## Injection

Input from users, files, network or environment is hostile until checked.

- SQL: bound parameters or ORM only. No string building into a query, `ORDER BY` and column names included: pick
  them from an allowlist.
- Commands: no shell. Argument list (`subprocess.run([...])`, `execFile`, `ProcessBuilder(list)`,
  `Command::new(..).arg(..)`). On Windows a `.bat` or `.cmd` target goes through `cmd.exe` even then: avoid batch
  files or allowlist their arguments.
- LDAP, XPath, NoSQL operators, expression languages (SpEL, OGNL, EL), server templates: no input interpreted.
  A template is never built from input.
- No `eval`, `exec`, `new Function`, `vm` (not a sandbox) or `loadstring` on input.
- Logs: strip `\r` and `\n` from logged input.

## Files and paths

Resolve first, then check the result stays under the allowed folder.

- Python `Path(base, name).resolve()` then `is_relative_to(base)`; Java `toRealPath()` then `Path.startsWith`;
  Node `path.resolve` then compare with `base + path.sep`. A string prefix check lets `/base-evil` through.
- Absolute input replaces the base in `os.path.join`, `pathlib`, Rust `Path::join` and Java `resolve`.
- Temporary files: `tempfile.mkstemp`, `NamedTemporaryFile` or `TemporaryDirectory`, `Files.createTempFile`,
  `fs.mkdtemp`. Never a fixed path under `/tmp`, never `tempfile.mktemp`.
- Sensitive files 600, folders 700.
- Archives: check each entry against `../` and absolute names (zip slip), cap total unpacked size. Python
  `tarfile`: `extractall(filter="data")`.
- Uploads: allowlist of types checked on content, random stored name, outside the web root, size cap.

## Deserialisation and parsing

Data from outside is parsed as data, never as objects.

- Never native deserialisation of untrusted bytes: `pickle`, `marshal`, `shelve`, `yaml.load` without
  `SafeLoader`, `ObjectInputStream`, PHP `unserialize`, .NET `BinaryFormatter`. JSON with a schema,
  `yaml.safe_load`.
- XML: DTD and external entities off (XXE); Python `defusedxml`.
- Regex on input: no nested quantifiers that backtrack (ReDoS), or a length cap before matching.

## Access and web

Every request is checked on the server, whatever the client shows.

- Authorisation on each action and each object id (no access by guessing an id).
- SSRF: allowlist of hosts and schemes for any URL from input; refuse loopback, private, link-local
  (`169.254.169.254`) and IPv6 equivalents after DNS resolution, connect to the address checked, no redirect to
  another host.
- No open redirect to a URL from input.
- CORS: never reflect the request's `Origin` with credentials; allowlist origins.
- Session cookies `HttpOnly`, `Secure`, `SameSite`; CSRF token on every state change with cookie auth.
- HTML output escaped by the template engine for its context; raw HTML only after a sanitiser.
- JWT: signature verified, algorithm pinned, `none` refused, expiry checked.

## Cryptography

Vetted libraries only, never home-made crypto.

- Symmetric: AES-256-GCM (or ChaCha20-Poly1305) with a random 12-byte nonce, never reused with one key. Never ECB,
  never CBC without MAC, never a fixed IV.
- Passwords: Argon2id, scrypt or bcrypt with a per-user salt. Never MD5, SHA-1 or plain SHA-256.
- Security randomness (tokens, keys, IVs, session ids): `secrets`, `crypto.randomBytes`,
  `crypto.getRandomValues`, `SecureRandom`, `crypto/rand`, `random_bytes`. Never `random`, `Math.random`,
  `java.util.Random`, `rand()`.
- Keys: RSA 3072 bits (2048 at least), curves P-256 or Ed25519.
- TLS: certificate and host name checks always on, tests included.
- Secret comparison in constant time: `hmac.compare_digest`, `crypto.timingSafeEqual`, `MessageDigest.isEqual`,
  `hash_equals`.

## Secrets and configuration

Nothing secret lives in the code.

- No password, token or key in code, tests or examples: environment or secret manager, sample entry in
  `.env.example`.
- Debug off by default, no stack trace sent to the client.
- No password, token or personal data in logs.

Secret search when no secret scanner ran, from the project root:

```
rg -n -i --hidden -g '!.git/' -g '!node_modules/' -e '(api[_-]?key|secret|token|passw(or)?d)[\x22\x27]?\s*[:=]\s*[\x22\x27][^\x22\x27\s]{8,}' -e '-----BEGIN [A-Z ]*PRIVATE KEY-----' -e '(?-i)AKIA[0-9A-Z]{16}' -e 'gh[pousr]_[A-Za-z0-9]{36}' -e 'xox[abprs]-[A-Za-z0-9-]{10,}' .
```

## Concurrency

Shared state is guarded, and the guard stays short.

- Java double-checked locking only with `volatile`.
- Never lock on a shared or value object (`Boolean`, `Integer`, string literal).
- No lock held during sleep, I/O or a network call.
- Shared collections: concurrent types or guarded access.
- Check-then-act on files and resources (TOCTOU): open once, act on the handle.

## Resources and errors

Failures end cleanly and inputs have limits.

- Resources closed on every path: `with`, try-with-resources, `defer`, `using`.
- No swallowed exception, no catch-all without reason.
- Caps on request size, upload size, item counts and recursion depth; timeouts on outgoing calls.

## By language

Items scanners often miss in each stack.

- Node and TypeScript: prototype pollution through merging input (`__proto__`, `constructor`): `Map`,
  `Object.create(null)` or key allowlist; `dangerouslySetInnerHTML`, `v-html` and `bypassSecurityTrust*` only
  on sanitised HTML; `child_process.exec` replaced by `execFile`; body size limit on the server.
- Python: `requests` and `httpx` calls with a `timeout`, `verify` left on; Django and Flask with `DEBUG` off and
  `SECRET_KEY` from environment; `mark_safe` and `|safe` only on trusted HTML; ORM `raw()` with parameters.
- PHP and WordPress: `$wpdb->prepare()` for every query with a variable; input through `sanitize_*` or `absint`,
  output through `esc_html`, `esc_attr`, `esc_url` or `wp_kses`; nonce check plus `current_user_can()` on every
  form, AJAX action and admin page (a nonce is not authorisation); REST routes with a real
  `permission_callback`; `password_hash` and `password_verify`; no `include` of a path from input.
- Rust: each `unsafe` block small and justified; `checked_*` or `saturating_*` arithmetic on sizes from input
  (release builds wrap); no `unwrap()` on input in a server (panic = denial of service).
- Luau and Roblox: server never trusts the client; every `RemoteEvent` and `RemoteFunction` handler checks type,
  range, NaN (`x ~= x`) and rate of each argument and whether this player may act (ownership, distance,
  cooldown); client sends intent, server computes money, damage and inventory; nothing secret in
  `ReplicatedStorage` or client scripts; no `InvokeClient` waited on by the server; no `require` of an outside
  asset id and no `loadstring`; API keys through the secrets store of `HttpService` on the server only; text
  shown to others filtered with `TextService`.

## Advisory sources

Machine sources run in `scan.py`; the web step of the procedure reads the others.

- OSV (`api.osv.dev`): every ecosystem, used by `scan.py` for packages pinned from public registries.
- GitHub Advisory Database (`github.com/advisories`) and NVD (`nvd.nist.gov`): CVE details and fixed versions.
- RustSec, the Go vulnerability database (`vuln.go.dev`), FriendsOfPHP security advisories for Packagist.
- WordPress core and plugins: WPScan, Wordfence Intelligence, Patchstack.
- Runtimes and frameworks: the vendor's security release page (Node.js, Python, PHP, Django, Spring).
- Wally packages and the Roblox engine: no advisory database; read the package's releases and issues.
