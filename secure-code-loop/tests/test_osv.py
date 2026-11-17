import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "lib"))

import osv
from parsers import CRITICAL, HIGH, LOW, MEDIUM

CARGO_LOCK = """
[[package]]
name = "smallvec"
version = "1.6.0"
source = "registry+https://github.com/rust-lang/crates.io-index"

[[package]]
name = "local"
version = "0.1.0"

[[package]]
name = "forked"
version = "2.0.0"
source = "git+https://example.invalid/forked"
"""
POETRY_LOCK = """
[[package]]
name = "pyyaml"
version = "5.3"

[[package]]
name = "private"
version = "1.0"
[package.source]
type = "legacy"
url = "https://pypi.example.invalid/simple"
"""
UV_LOCK = """
[[package]]
name = "jinja2"
version = "2.10"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "mine"
version = "0.1.0"
source = { editable = "." }
"""
NPM_LOCK = {"packages": {
    "": {"name": "app"},
    "node_modules/lodash": {"version": "4.17.15", "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.15.tgz"},
    "node_modules/a/node_modules/@scope/b": {"version": "1.0.0",
                                             "resolved": "https://registry.npmjs.org/@scope/b/-/b-1.0.0.tgz"},
    "node_modules/inhouse": {"version": "3.0.0", "resolved": "https://npm.example.invalid/inhouse-3.0.0.tgz"}}}
COMPOSER_LOCK = {"packages": [{"name": "guzzlehttp/guzzle", "version": "v7.4.0",
                               "notification-url": "https://packagist.org/downloads/"}],
                 "packages-dev": [{"name": "acme/private", "version": "1.0.0"}]}
FILES = {"Cargo.lock": CARGO_LOCK, "poetry.lock": POETRY_LOCK, "uv.lock": UV_LOCK,
         "web/package-lock.json": json.dumps(NPM_LOCK), "composer.lock": json.dumps(COMPOSER_LOCK),
         "requirements.txt": "PyYAML==5.3\nrequests>=2.0\nDjango[argon2] == 3.2.1 ; python_version > '3'\n",
         "requirements-private.txt": "--index-url https://pypi.example.invalid/simple\nsecret==1.0\n",
         "README.md": "PyYAML==5.3\n"}


class Inventory(unittest.TestCase):
    def test_only_packages_pinned_from_public_registries_are_listed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, text in FILES.items():
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(text, encoding="utf-8")
            found = osv.inventory(root, sorted(FILES))
        self.assertEqual(sorted(found), sorted([
            ("Cargo.lock", "crates.io", "smallvec", "1.6.0"), ("poetry.lock", "PyPI", "pyyaml", "5.3"),
            ("uv.lock", "PyPI", "jinja2", "2.10"), ("composer.lock", "Packagist", "guzzlehttp/guzzle", "7.4.0"),
            ("web/package-lock.json", "npm", "lodash", "4.17.15"),
            ("web/package-lock.json", "npm", "@scope/b", "1.0.0"),
            ("requirements.txt", "PyPI", "PyYAML", "5.3"), ("requirements.txt", "PyPI", "Django", "3.2.1")]))

    def test_unreadable_lockfiles_give_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "Cargo.lock").write_text("not [ toml", encoding="utf-8")
            self.assertEqual(osv.inventory(Path(folder), ["Cargo.lock", "requirements.txt"]), [])


def vuln(ident, **fields):
    return {"id": ident, "summary": f"{ident} summary", **fields}


class Severity(unittest.TestCase):
    def test_named_severity(self):
        self.assertEqual(osv.named_severity(vuln("MAL-2024-1")), CRITICAL)
        self.assertEqual(osv.named_severity(vuln("GHSA-a", database_specific={"severity": "MODERATE"})), MEDIUM)
        self.assertEqual(osv.named_severity(vuln("RUSTSEC-1", affected=[
            {"database_specific": {"informational": "unmaintained"}}])), LOW)
        self.assertIsNone(osv.named_severity(vuln("PYSEC-1")))

    def test_an_alias_lends_its_severity_and_unknown_is_high(self):
        found = osv.package_findings("requirements.txt", ("PyPI", "PyYAML", "5.3"), [
            vuln("PYSEC-1", aliases=["GHSA-b"]),
            vuln("GHSA-b", database_specific={"severity": "CRITICAL"}),
            vuln("PYSEC-2")])
        self.assertEqual([(raw.ident, raw.level) for raw in found],
                         [("PYSEC-1", CRITICAL), ("GHSA-b", CRITICAL), ("PYSEC-2", HIGH)])

    def test_every_fix_of_the_package_is_named(self):
        found = osv.package_findings("requirements.txt", ("PyPI", "PyYAML", "5.3"), [
            vuln(ident, affected=[{"package": {"name": "PyYAML"}, "ranges": [{"events": [{"fixed": fixed}]}]}])
            for ident, fixed in (("PYSEC-1", "5.4"), ("PYSEC-2", "5.3.1"))])
        self.assertEqual({raw.message.rsplit(", fix ", 1)[1] for raw in found}, {"5.3.1, 5.4"})

    def test_fixes_come_from_the_ranges_of_this_package(self):
        record = vuln("GHSA-c", affected=[
            {"package": {"name": "pyyaml"}, "ranges": [{"events": [{"introduced": "0"}, {"fixed": "5.4"}]}]},
            {"package": {"name": "other"}, "ranges": [{"events": [{"fixed": "9.9"}]}]}])
        self.assertEqual(osv.fixes(record, "PyYAML"), ["5.4"])

    def test_parse_skips_withdrawn_records(self):
        data = {"packages": 3, "hits": [{"lockfile": "Cargo.lock", "package": ["crates.io", "smallvec", "1.6.0"],
                                         "vulns": [vuln("RUSTSEC-1"), vuln("RUSTSEC-2", withdrawn="2024-01-01")]}]}
        found = osv.parse(data, ".")
        self.assertEqual([(raw.tool, raw.ident, raw.path, raw.topic) for raw in found],
                         [("osv", "RUSTSEC-1", "Cargo.lock", "package:smallvec")])
        self.assertEqual(found[0].message, "smallvec: 1.6.0 RUSTSEC-1 summary, fix none")


if __name__ == "__main__":
    unittest.main()
