import re
from collections import namedtuple

from common import last_line

LEVELS = SECRET, BLOCKER, CRITICAL, HIGH, MEDIUM, LOW, INFO = (
    "secret", "blocker", "critical", "high", "medium", "low", "info")
SEVERITIES = {"BLOCKER": BLOCKER, "CRITICAL": CRITICAL, "HIGH": HIGH, "ERROR": HIGH, "MAJOR": MEDIUM,
              "MEDIUM": MEDIUM, "MODERATE": MEDIUM, "WARNING": MEDIUM, "MINOR": LOW, "LOW": LOW, "INFO": INFO}
SECRET_CWE = "798"
CWE = re.compile(r"(?:CWE-)?(\d+)", re.IGNORECASE)
SECURITY_QUALITIES = ("SECURITY", "RELIABILITY")
BANDIT_CWE = {"B506": "502"}
OK = "ok"
Raw = namedtuple("Raw", "tool ident level path line message topic")


def level(value):
    return SEVERITIES.get(str(value or "").upper(), MEDIUM)


def most_severe(levels):
    return min(levels, key=LEVELS.index) if levels else LOW


def cwe(value):
    for item in value if isinstance(value, list) else [value]:
        match = CWE.match(str(item).strip()) if item not in (None, "") else None
        if match:
            return match.group(1)
    return None


def verdict(data, code, text):
    if data is None:
        return f"failed: exit {code}, {last_line(text)}"
    error = data.get("error") if isinstance(data, dict) else None
    if error:
        detail = error.get("summary") or error.get("message") or error.get("code") if isinstance(error, dict) else error
        return f"failed: {detail}"
    errors = data.get("errors") if isinstance(data, dict) else None
    return f"{OK}, {len(errors)} scan errors" if errors else OK


def first_number(value):
    match = re.match(r"\d+", str(value or ""))
    return int(match.group(0)) if match else 0


def joined(place, name):
    return f"{place}/{name}" if place not in ("", ".") else name


def package_finding(tool, lockfile, package, advisory):
    ident, severity, text = advisory
    return Raw(tool, ident, severity, lockfile, 0, f"{package}: {text}", f"package:{package}")


def semgrep(data, place):
    found = []
    for item in data.get("results") or []:
        extra = item.get("extra") or {}
        found.append(Raw("semgrep", item.get("check_id", ""), level(extra.get("severity")), item.get("path", ""),
                         (item.get("start") or {}).get("line", 0), extra.get("message", ""),
                         cwe((extra.get("metadata") or {}).get("cwe"))))
    return found


def gitleaks(data, place):
    return [Raw("gitleaks", item.get("RuleID", ""), SECRET, item.get("File", ""), item.get("StartLine", 0),
                item.get("Description", ""), SECRET_CWE) for item in data if isinstance(item, dict)]


def trivy_result(result):
    target, found = result.get("Target", ""), []
    for item in result.get("Vulnerabilities") or []:
        text = f"{item.get('InstalledVersion', '')} {item.get('Title', '')}, fix {item.get('FixedVersion') or 'none'}"
        found.append(package_finding("trivy", target, item.get("PkgName", ""),
                                     (item.get("VulnerabilityID", ""), level(item.get("Severity")), text)))
    for item in result.get("Misconfigurations") or []:
        if item.get("Status", "FAIL") == "FAIL":
            found.append(Raw("trivy", item.get("ID", ""), level(item.get("Severity")), target,
                             (item.get("CauseMetadata") or {}).get("StartLine", 0),
                             f"{item.get('Title', '')}: {item.get('Message', '')}", item.get("ID")))
    for item in result.get("Secrets") or []:
        found.append(Raw("trivy", item.get("RuleID", ""), SECRET, target, item.get("StartLine", 0),
                         item.get("Title", ""), SECRET_CWE))
    return found


def trivy(data, place):
    return [raw for result in data.get("Results") or [] for raw in trivy_result(result)]


def bandit(data, place):
    return [Raw("bandit", item.get("test_id", ""), level(item.get("issue_severity")), item.get("filename", ""),
                item.get("line_number", 0), item.get("issue_text", ""),
                BANDIT_CWE.get(item.get("test_id")) or cwe((item.get("issue_cwe") or {}).get("id")))
            for item in data.get("results") or []]


def gosec(data, place):
    return [Raw("gosec", item.get("rule_id", ""), level(item.get("severity")), item.get("file", ""),
                first_number(item.get("line")), item.get("details", ""), cwe((item.get("cwe") or {}).get("id")))
            for item in data.get("Issues") or []]


def cargo_audit(data, place):
    lockfile, found = joined(place, "Cargo.lock"), []
    for item in (data.get("vulnerabilities") or {}).get("list") or []:
        advisory, package = item.get("advisory") or {}, item.get("package") or {}
        fixes = ", ".join((item.get("versions") or {}).get("patched") or []) or "none"
        text = f"{package.get('version', '')} {advisory.get('title', '')}, fix {fixes}"
        found.append(package_finding("cargo-audit", lockfile, package.get("name", ""),
                                     (advisory.get("id", ""), HIGH, text)))
    for kind, items in (data.get("warnings") or {}).items():
        for item in items or []:
            package, advisory = item.get("package") or {}, item.get("advisory") or {}
            found.append(package_finding("cargo-audit", lockfile, package.get("name", ""),
                                         (advisory.get("id", kind), LOW, f"{package.get('version', '')} {kind}")))
    return found


def fix_text(value):
    if isinstance(value, dict):
        major = " (major)" if value.get("isSemVerMajor") else ""
        return f"{value.get('name', '')}@{value.get('version', '')}{major}"
    return "available" if value else "none"


def npm_audit(data, place):
    lockfile, found = joined(place, "package-lock.json"), []
    for name, item in (data.get("vulnerabilities") or {}).items():
        advisories = [via for via in item.get("via") or [] if isinstance(via, dict)]
        idents = ",".join(str(via.get("url", "")).rsplit("/", 1)[-1] for via in advisories) or "via dependency"
        title = advisories[0].get("title", "") if advisories else "depends on a vulnerable package"
        text = f"{item.get('range', '')} {title}, fix {fix_text(item.get('fixAvailable'))}"
        found.append(package_finding("npm-audit", lockfile, name, (idents, level(item.get("severity")), text)))
    return found


def pnpm_audit(data, place):
    lockfile = joined(place, "pnpm-lock.yaml")
    return [package_finding("pnpm-audit", lockfile, item.get("module_name", ""),
                            (item.get("github_advisory_id") or str(item.get("id", "")), level(item.get("severity")),
                             f"{item.get('vulnerable_versions', '')} {item.get('title', '')}, "
                             f"fix {item.get('patched_versions') or 'none'}"))
            for item in (data.get("advisories") or {}).values()]
