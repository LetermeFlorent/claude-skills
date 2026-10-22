import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
sys.path.insert(0, str(HERE / "checks" / "project"))

from common import ENCODING, FAILED, guard, read_json
from runs import FINDINGS, PLAN, latest_run, project_root
from store import CONFIRMED, SECRET
from repository import SIGNED

MARKER = "<!-- clean-code plan v1 -->"
PHASES = {12: 1, 9: 2, 0: 3, 3: 3, 7: 3, 8: 3, 13: 3, 14: 3, 15: 3, 16: 3, 17: 3, 18: 3, 19: 3, 5: 4, 6: 4,
          1: 5, 2: 5, 4: 5, 10: 6, 11: 6}
SECRET_PHASE = 6
YES, NO, NOTHING = "oui", "non", "aucun"
FIELDS = ("Phase", "Constats", "Sure", "Fichiers", "Verification", "Commit")
STEP = re.compile(r"^## Etape (\d+) : (.+)$", re.MULTILINE)
KEPT = re.compile(r"^## Laisse tel quel\s*$", re.MULTILINE)
KEPT_LINE = re.compile(r"^- ([MR]\d+) : (.*)$", re.MULTILINE)
PLACEHOLDER = re.compile(r"<[^<>\n]{2,120}>")
FORBIDDEN_PATHS = re.compile(r"(^|/)(\.ia|\.claude)(/|$)|(^|/)CLAUDE\.md$")
BAD_CHARS = {chr(0x2014): "em dash", chr(0x201C): "curly quote", chr(0x201D): "curly quote",
             chr(0x2019): "curly apostrophe", chr(0xA0): "no-break space", chr(0x202F): "narrow no-break space"}


def _phase(finding):
    return SECRET_PHASE if finding.get("cap") == SECRET else PHASES[finding["rule"]]


def _fields(body):
    return {name: value.strip() for name, value in re.findall(r"^(\w+) : (.*)$", body, re.MULTILINE) if name in FIELDS}


def _ids(text):
    return [part.strip() for part in text.split(",") if part.strip() and part.strip() != NOTHING]


def _line(text, index):
    return text.count("\n", 0, index) + 1


def _step(number, fields, findings, state):
    problems, last_phase = state["problems"], state["phase"]
    missing = [name for name in FIELDS if not fields.get(name)]
    if missing:
        problems.append(f"step {number}: missing {', '.join(missing)}")
        return []
    phase = int(fields["Phase"]) if fields["Phase"].isdigit() else 0
    if phase not in set(PHASES.values()):
        problems.append(f"step {number}: phase {fields['Phase']} is not 1 to 6")
    elif phase < last_phase:
        problems.append(f"step {number}: phase {phase} comes after phase {last_phase}")
    if fields["Sure"] not in (YES, NO):
        problems.append(f"step {number}: Sure is oui or non, not {fields['Sure']}")
    ids = _ids(fields["Constats"])
    for wanted in ids:
        finding = findings.get(wanted)
        if finding and _phase(finding) != phase:
            problems.append(f"step {number}: {wanted} (rule {finding['rule']}) belongs to phase {_phase(finding)}")
    for path in _ids(fields["Fichiers"]):
        if FORBIDDEN_PATHS.search(path.replace("\\", "/")):
            problems.append(f"step {number}: {path} is an AI tooling path and is never committed")
    state["phase"] = max(phase, last_phase)
    return ids


def check(text, findings):
    problems = [] if text.startswith(MARKER) else [f"first line must be {MARKER}"]
    holes = sorted(set(PLACEHOLDER.findall(text)))
    problems += [f"template placeholder left: {hole}" for hole in holes if hole[1] != "!"]
    problems += [f"{name} at line {_line(text, text.index(char))}" for char, name in BAD_CHARS.items() if char in text]
    problems += [f"AI tool attribution at line {_line(text, hit.start())}" for hit in SIGNED.finditer(text)]
    kept_at = KEPT.search(text)
    if not kept_at:
        problems.append("the ## Laisse tel quel section is missing")
    plan = text[:kept_at.start()] if kept_at else text
    heads = list(STEP.finditer(plan))
    placed, safe, state = [], 0, {"problems": problems, "phase": 0}
    for index, head in enumerate(heads):
        number = int(head.group(1))
        if number != index + 1:
            problems.append(f"step {number} should be numbered {index + 1}")
        end = heads[index + 1].start() if index + 1 < len(heads) else len(plan)
        fields = _fields(plan[head.end():end])
        placed += _step(number, fields, findings, state)
        safe += fields.get("Sure") == YES
    kept = KEPT_LINE.findall(text[kept_at.end():]) if kept_at else []
    problems += [f"{wanted} left as is without a reason" for wanted, why in kept if not why.strip()]
    placed += [wanted for wanted, _ in kept]
    confirmed = {key for key, finding in findings.items() if finding["status"] == CONFIRMED}
    counts = Counter(placed)
    problems += [f"{wanted} appears {count} times" for wanted, count in sorted(counts.items()) if count > 1]
    problems += [f"{wanted} is not a confirmed finding" for wanted in sorted(set(counts) - confirmed)]
    unplanned = sorted(confirmed - set(counts))
    problems += [f"{wanted} is confirmed but neither planned nor left as is" for wanted in unplanned]
    return problems, len(heads), safe, len(kept)


def main():
    parser = argparse.ArgumentParser(description="Check a clean-code plan.md against the verified findings.")
    parser.add_argument("plan", nargs="?", help="plan.md, defaults to the one in the latest run")
    parser.add_argument("--run", help="run folder, defaults to the latest under .ia/clean-code")
    args = parser.parse_args()
    run = latest_run(project_root(Path.cwd()), args.run)
    path = Path(args.plan).resolve() if args.plan else run / PLAN
    payload = read_json(run / FINDINGS)
    findings = {finding["id"]: finding for finding in payload["findings"]}
    problems, steps, safe, kept = check(path.read_text(encoding=ENCODING), findings)
    if ".ia/clean-code/" not in path.as_posix():
        problems.insert(0, f"{path} must live in .ia/clean-code/<run>/")
    if problems:
        print(f"plan refused, {len(problems)} problems:")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(FAILED)
    print(f"plan ok: {steps} steps, {safe} safe, {kept} left as is")


if __name__ == "__main__":
    guard(main, "tick every confirmed id against the plan by hand and check the phase order of SKILL.md")
