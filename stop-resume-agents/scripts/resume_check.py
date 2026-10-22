import argparse
import os
import re
import sys

MARKER = "<!-- stop-resume-agents v1 -->"
FIELDS = ("Type :", "Statut :", "A relancer :", "Reponse a l'arret :", "Ordre de relance :",
          "Fichiers qu'il possede :", "### Consigne de depart")
STATES = r"^Etat : (ARRET EN COURS|ARRETE|REPRIS|REMPLACE)"
PENDING = re.compile(r"(^|: |, )(en attente|a decider|a remplir)(\s+\S+)?\s*$")
NO_PROMPT = ("PROMPT NOT FOUND", "PROMPT INTROUVABLE")
BAD_CHARS = {chr(0x2014): "em dash", chr(0x201C): "curly quote", chr(0x201D): "curly quote",
             chr(0x2019): "curly apostrophe", chr(0xA0): "no-break space", chr(0x202F): "narrow no-break space"}


def template_placeholders():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resume-template.md")
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return {"<id>", "<date>", "<chemin absolu>", "<description>"}
    return {p for p in re.findall(r"<[^<>\n]{2,120}>", text) if not p.startswith("<!--")}


def mask_fences(text):
    masked, blocks, fence, body = [], [], "", []
    for line in text.split("\n"):
        ticks = re.match(r"^(`{3,})", line)
        if not fence and ticks:
            fence, body = ticks.group(1), []
            masked.append(line)
        elif fence and re.match("^" + fence + r"`*\s*$", line):
            blocks.append("\n".join(body).strip())
            masked += (["(code)"] if blocks[-1] else []) + [line]
            fence = ""
        elif fence:
            body.append(line)
        else:
            masked.append(line)
    if fence:
        masked.append("(unclosed code block)")
    return "\n".join(masked), blocks


def check_agent(agent, body, raw):
    problems = [f"agent {agent}: missing '{f}'" for f in FIELDS if f not in body]
    if re.search(r"### Consigne de depart\s*\n+`{3,}text\s*\n`{3,}", body):
        problems.append(f"agent {agent}: original prompt block is empty")
    if any(token in raw for token in NO_PROMPT) and "Consigne perdue :" not in body:
        problems.append(f"agent {agent}: original prompt not found. Recover it from your context or the "
                        "parent's transcript, else write 'Consigne perdue : <why>' under the block")
    return problems


def agent_sections(text):
    masked, _ = mask_fences(text)
    raw_parts = re.split(r"^## (?=Agent \S)", text, flags=re.M)
    found = {}
    for part in re.split(r"^## ", masked, flags=re.M):
        match = re.match(r"Agent (\S+)", part)
        if match:
            raw = next((r for r in raw_parts if r.startswith(f"Agent {match.group(1)}")), part)
            found[match.group(1)] = (part, raw)
    return found


def check(text, agents):
    if not text:
        return ["file is empty or unreadable"]
    masked, blocks = mask_fences(text)
    problems = [] if text.startswith(MARKER) else ["first line is not the stop-resume-agents marker"]
    if "(unclosed code block)" in masked:
        problems.append("a code block is never closed")
    state = re.search(STATES, masked, re.M)
    if not state:
        problems.append("no valid 'Etat :' line")
    found = agent_sections(text)
    problems += [f"agent {a} has no '## Agent {a}' section" for a in agents if a not in found]
    for agent, (body, raw) in found.items():
        problems += check_agent(agent, body, raw)
    if state and state.group(1) != "ARRET EN COURS":
        problems += [f"still pending: {l.strip()}" for l in masked.split("\n") if PENDING.search(l)]
        if any(re.match(r"(en attente|a remplir)\b", block) for block in blocks):
            problems.append("a code block still says 'en attente'")
    left = sorted(p for p in template_placeholders() if p in masked or p in blocks)
    problems += [f"template placeholder left: {p}" for p in left]
    problems += [f"forbidden character outside code blocks: {n}" for c, n in BAD_CHARS.items() if c in masked]
    return problems


def main():
    parser = argparse.ArgumentParser(description="Check a resume.md written by /stop-all.")
    parser.add_argument("path")
    parser.add_argument("--agent", action="append", default=[], help="agent id expected, repeatable")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        with open(args.path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError as error:
        print(f"cannot read {args.path}: {error}")
        sys.exit(1)
    problems = check(text, args.agent)
    print("\n".join(problems) if problems else f"OK: {args.path}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f"resume_check failed: {error!r}. Check the file by hand against resume-template.md.", file=sys.stderr)
        sys.exit(2)
