import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "lib"))

import parsers
import sonar
from parsers import CRITICAL, HIGH, LOW, MEDIUM, SECRET, OK


def short(raws):
    return [(raw.tool, raw.ident, raw.level, raw.path, raw.line, raw.topic) for raw in raws]


class Code(unittest.TestCase):
    def test_semgrep(self):
        data = {"results": [{"check_id": "python.sql", "path": "app/db.py", "start": {"line": 7},
                             "extra": {"severity": "ERROR", "message": "sql",
                                       "metadata": {"cwe": ["CWE-89: SQL Injection"]}}}]}
        self.assertEqual(short(parsers.semgrep(data, ".")), [("semgrep", "python.sql", HIGH, "app/db.py", 7, "89")])

    def test_bandit_maps_unsafe_yaml_load_to_deserialisation(self):
        data = {"results": [{"test_id": "B506", "issue_severity": "MEDIUM", "filename": "./app/settings.py",
                             "line_number": 4, "issue_text": "yaml load", "issue_cwe": {"id": 20}},
                            {"test_id": "B602", "issue_severity": "HIGH", "filename": "app/net.py",
                             "line_number": 5, "issue_text": "shell", "issue_cwe": {"id": 78}}]}
        self.assertEqual([(raw.ident, raw.level, raw.topic) for raw in parsers.bandit(data, ".")],
                         [("B506", MEDIUM, "502"), ("B602", HIGH, "78")])

    def test_gosec_takes_the_first_line_of_a_range(self):
        data = {"Issues": [{"rule_id": "G204", "severity": "MEDIUM", "file": "main.go", "line": "12-14",
                            "details": "subprocess", "cwe": {"id": "78"}}]}
        self.assertEqual(short(parsers.gosec(data, ".")), [("gosec", "G204", MEDIUM, "main.go", 12, "78")])

    def test_sonar_keeps_security_impacts_and_hotspots(self):
        data = {"key": "proj", "issues": [
            {"rule": "python:S2077", "component": "proj:app/db.py", "line": 7, "message": "sql",
             "impacts": [{"softwareQuality": "MAINTAINABILITY", "severity": "LOW"},
                         {"softwareQuality": "SECURITY", "severity": "BLOCKER"}]},
            {"rule": "python:S100", "component": "proj:app/net.py", "type": "CODE_SMELL", "severity": "MAJOR"}],
            "hotspots": [{"ruleKey": "python:S4790", "component": "proj:app/net.py", "line": 3,
                          "vulnerabilityProbability": "MEDIUM", "message": "hash"}]}
        self.assertEqual([(raw.level, raw.path) for raw in sonar.parse(data, ".")],
                         [("blocker", "app/db.py"), (LOW, "app/net.py"), (MEDIUM, "app/net.py")])


class Secrets(unittest.TestCase):
    def test_gitleaks(self):
        data = [{"RuleID": "generic-api-key", "File": "app/settings.py", "StartLine": 1, "Description": "key"}]
        self.assertEqual(short(parsers.gitleaks(data, ".")),
                         [("gitleaks", "generic-api-key", SECRET, "app/settings.py", 1, "798")])

    def test_trivy_vulnerabilities_misconfigurations_and_secrets(self):
        data = {"Results": [{"Target": "requirements.txt", "Vulnerabilities": [
            {"VulnerabilityID": "CVE-1", "PkgName": "pyyaml", "InstalledVersion": "5.3", "FixedVersion": "5.4",
             "Severity": "CRITICAL", "Title": "code execution"}]},
            {"Target": "Dockerfile", "Misconfigurations": [
                {"ID": "DS002", "Severity": "HIGH", "Status": "FAIL", "CauseMetadata": {"StartLine": 2}},
                {"ID": "DS001", "Severity": "LOW", "Status": "PASS"}]},
            {"Target": ".env", "Secrets": [{"RuleID": "aws-key", "StartLine": 3, "Title": "AWS key"}]}]}
        self.assertEqual(short(parsers.trivy(data, ".")),
                         [("trivy", "CVE-1", CRITICAL, "requirements.txt", 0, "package:pyyaml"),
                          ("trivy", "DS002", HIGH, "Dockerfile", 2, "DS002"),
                          ("trivy", "aws-key", SECRET, ".env", 3, "798")])


class Packages(unittest.TestCase):
    def test_cargo_audit_vulnerabilities_are_high_and_warnings_low(self):
        data = {"vulnerabilities": {"list": [{"advisory": {"id": "RUSTSEC-1", "title": "overflow"},
                                              "package": {"name": "smallvec", "version": "1.6.0"},
                                              "versions": {"patched": [">=1.6.1"]}}]},
                "warnings": {"unmaintained": [{"package": {"name": "old", "version": "0.1"},
                                               "advisory": {"id": "RUSTSEC-2"}}]}}
        found = parsers.cargo_audit(data, "crates/core")
        self.assertEqual(short(found), [("cargo-audit", "RUSTSEC-1", HIGH, "crates/core/Cargo.lock", 0,
                                         "package:smallvec"),
                                        ("cargo-audit", "RUSTSEC-2", LOW, "crates/core/Cargo.lock", 0, "package:old")])
        self.assertIn("fix >=1.6.1", found[0].message)

    def test_npm_audit_names_the_advisory_and_the_fix(self):
        data = {"vulnerabilities": {
            "lodash": {"severity": "high", "range": "<4.17.21", "fixAvailable": True,
                       "via": [{"url": "https://github.com/advisories/GHSA-35jh-r3h4-6jhm", "title": "injection"}]},
            "wrapper": {"severity": "moderate", "via": ["lodash"],
                        "fixAvailable": {"name": "wrapper", "version": "2.0.0", "isSemVerMajor": True}}}}
        found = parsers.npm_audit(data, ".")
        self.assertEqual([(raw.ident, raw.level, raw.path) for raw in found],
                         [("GHSA-35jh-r3h4-6jhm", HIGH, "package-lock.json"),
                          ("via dependency", MEDIUM, "package-lock.json")])
        self.assertTrue(found[1].message.endswith("fix wrapper@2.0.0 (major)"))

    def test_pnpm_audit(self):
        data = {"advisories": {"1": {"module_name": "minimist", "github_advisory_id": "GHSA-x", "severity": "critical",
                                     "vulnerable_versions": "<1.2.6", "patched_versions": ">=1.2.6"}}}
        self.assertEqual(short(parsers.pnpm_audit(data, "web")),
                         [("pnpm-audit", "GHSA-x", CRITICAL, "web/pnpm-lock.yaml", 0, "package:minimist")])


class Verdict(unittest.TestCase):
    def test_states(self):
        self.assertEqual(parsers.verdict({"results": []}, 1, ""), OK)
        self.assertEqual(parsers.verdict({"results": [], "errors": [{}, {}]}, 1, ""), f"{OK}, 2 scan errors")
        self.assertEqual(parsers.verdict({"error": {"summary": "no lockfile"}}, 1, ""), "failed: no lockfile")
        self.assertEqual(parsers.verdict(None, 3, "first\nboom\n"), "failed: exit 3, boom")

    def test_levels(self):
        self.assertEqual([parsers.level(name) for name in ("warning", "MAJOR", "minor", "unknown", None)],
                         [MEDIUM, MEDIUM, LOW, MEDIUM, MEDIUM])
        self.assertEqual(parsers.most_severe([LOW, SECRET, HIGH]), SECRET)
        self.assertEqual(parsers.cwe(["none", "CWE-79"]), "79")


if __name__ == "__main__":
    unittest.main()
