import json
import re
import urllib.request
from pathlib import PurePosixPath

try:
    import tomllib
except ImportError:
    tomllib = None

from common import ENCODING, read_json
from parsers import CRITICAL, HIGH, LOW, level, package_finding

API = "https://api.osv.dev/v1"
BATCH_LIMIT = 1000
HTTP_TIMEOUT = 30
CRATES = ("registry+https://github.com/rust-lang/crates.io-index", "sparse+https://index.crates.io/")
PYPI_SIMPLE = "https://pypi.org/simple"
PACKAGIST = "https://packagist.org/downloads/"
NPM_REGISTRY = "https://registry.npmjs.org/"
PIN = re.compile(r"^([A-Za-z0-9][\w.-]*)(?:\[[^\]]*\])?\s*==\s*([^\s;#\\]+)")
INDEX_OPTION = re.compile(r"^\s*(-i|--index-url|--extra-index-url)\b")
REQUIREMENTS = re.compile(r"^requirements[\w.-]*\.txt$")
MALICIOUS = "MAL-"


def toml(path):
    try:
        return tomllib.loads(path.read_text(encoding=ENCODING)) if tomllib else {}
    except (OSError, ValueError):
        return {}


def cargo(path):
    return [("crates.io", item.get("name"), item.get("version")) for item in toml(path).get("package") or []
            if str(item.get("source", "")).startswith(CRATES)]


def poetry(path):
    return [("PyPI", item.get("name"), item.get("version")) for item in toml(path).get("package") or []
            if "source" not in item]


def uv(path):
    return [("PyPI", item.get("name"), item.get("version")) for item in toml(path).get("package") or []
            if str((item.get("source") or {}).get("registry", "")).rstrip("/") == PYPI_SIMPLE]


def composer(path):
    data = read_json(path) or {}
    return [("Packagist", item.get("name"), str(item.get("version", "")).lstrip("v"))
            for group in ("packages", "packages-dev") for item in data.get(group) or []
            if item.get("notification-url") == PACKAGIST]


def npm(path):
    packages = (read_json(path) or {}).get("packages") or {}
    return [("npm", name.rsplit("node_modules/", 1)[-1], item.get("version")) for name, item in packages.items()
            if name and str(item.get("resolved", "")).startswith(NPM_REGISTRY)]


def requirements(path):
    try:
        lines = path.read_text(encoding=ENCODING).splitlines()
    except OSError:
        return []
    if any(INDEX_OPTION.match(line) for line in lines):
        return []
    return [("PyPI", match.group(1), match.group(2)) for match in map(PIN.match, lines) if match]


READERS = {"Cargo.lock": cargo, "poetry.lock": poetry, "uv.lock": uv, "composer.lock": composer,
           "package-lock.json": npm}


def inventory(root, names):
    found = []
    for name in names:
        base = PurePosixPath(name).name
        reader = READERS.get(base) or (requirements if REQUIREMENTS.match(base) else None)
        if reader:
            found += [(name, *package) for package in reader(root / name) if package[1] and package[2]]
    return found


def call(path, body=None):
    data = json.dumps(body).encode(ENCODING) if body is not None else None
    request = urllib.request.Request(f"{API}{path}", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as answer:
        return json.loads(answer.read().decode(ENCODING))


def vulnerable(packages):
    unique, found = sorted(set(packages)), {}
    for start in range(0, len(unique), BATCH_LIMIT):
        chunk = unique[start:start + BATCH_LIMIT]
        queries = [{"package": {"ecosystem": ecosystem, "name": name}, "version": version}
                   for ecosystem, name, version in chunk]
        for package, result in zip(chunk, call("/querybatch", {"queries": queries}).get("results") or []):
            found[package] = [vuln.get("id") for vuln in result.get("vulns") or [] if vuln.get("id")]
    return found


def named_severity(vuln):
    if vuln.get("id", "").startswith(MALICIOUS):
        return CRITICAL
    places = [vuln] + list(vuln.get("affected") or [])
    if any((place.get("database_specific") or {}).get("informational") for place in places):
        return LOW
    for place in places:
        for field in ("database_specific", "ecosystem_specific"):
            value = (place.get(field) or {}).get("severity")
            if isinstance(value, str) and value:
                return level(value)
    return None


def fixes(vuln, name):
    return sorted({event["fixed"] for affected in vuln.get("affected") or []
                   if str((affected.get("package") or {}).get("name", "")).lower() == name.lower()
                   for span in affected.get("ranges") or [] for event in span.get("events") or [] if "fixed" in event})


def package_findings(lockfile, package, vulns):
    _, name, version = package
    known = {vuln["id"]: named_severity(vuln) for vuln in vulns if named_severity(vuln)}
    every = ", ".join(sorted({fixed for vuln in vulns for fixed in fixes(vuln, name)})) or "none"
    found = []
    for vuln in vulns:
        severity = known.get(vuln["id"]) or next((known[alias] for alias in vuln.get("aliases") or []
                                                  if alias in known), HIGH)
        summary = vuln.get("summary") or str(vuln.get("details", "")).split("\n", 1)[0]
        text = f"{version} {summary}, fix {every}"
        found.append(package_finding("osv", lockfile, name, (vuln["id"], severity, text)))
    return found


def scan(root, names, output):
    listed = inventory(root, names)
    hits = vulnerable([entry[1:] for entry in listed])
    cache = {ident: call(f"/vulns/{ident}") for ident in sorted({i for ids in hits.values() for i in ids})}
    report = [{"lockfile": entry[0], "package": list(entry[1:]), "vulns": [cache[i] for i in hits.get(entry[1:], [])]}
              for entry in listed if hits.get(entry[1:])]
    output.write_text(json.dumps({"packages": len(listed), "hits": report}), encoding=ENCODING)


def parse(data, place):
    return [raw for hit in data.get("hits") or [] for raw in package_findings(
        hit["lockfile"], tuple(hit["package"]), [vuln for vuln in hit["vulns"] if not vuln.get("withdrawn")])]
