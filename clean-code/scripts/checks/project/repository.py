import re

from common import ENCODING, DECODE_ERRORS
from runs import REV_PARSE, git
from store import ATTRIBUTION
from words import AI_EMAILS, AI_SIGNATURE

RULE = 13
LISTED_BY = "git ls-files"
SIGNED = AI_SIGNATURE
RECORD, FIELD = chr(0x1E), chr(0x1F)
SHOWN = 5
BOT = re.compile(rf"{AI_EMAILS}|\(aider\)|\bcursor agent\b|\b(copilot|claude|codex|openai|anthropic|jules|devin"
                 r"|gemini|amazon-q|kiro)[\w-]*\[bot\]", re.IGNORECASE)
AI_BRANCH = re.compile(r"(^|/)(claude|codex|copilot|cursor|devin|jules|gemini|aider|windsurf|kiro|amazonq|openhands"
                       r"|cline|junie)[/-]", re.IGNORECASE)
AI_TRACKED = re.compile(r"(^|/)(\.claude/|CLAUDE(\.local)?\.md$|AGENTS?\.md$|GEMINI\.md$|\.cursorrules$|\.cursor/"
                        r"|\.windsurfrules$|\.windsurf/|\.devin/|\.github/copilot-instructions\.md$"
                        r"|\.github/instructions/|\.github/agents/|\.github/prompts/|\.aider[^/]*$|\.junie/"
                        r"|\.clinerules|\.roo/|\.kiro/|\.amazonq/|\.codex/|\.gemini/|\.continue/|\.ia/)")
WORKFLOW = re.compile(r"^\.github/workflows/.+\.ya?ml$", re.IGNORECASE)
AI_ACTION = re.compile(r"claude-code-action|claude-code-base-action|codex-action|run-gemini-cli|gemini-cli"
                       r"|copilot-swe-agent|devin|aider", re.IGNORECASE)
ENV_FILE = re.compile(r"(^|/)\.env(\.[\w-]+)?$")
ENV_SAMPLES = (".example", ".sample", ".template", ".dist")


def _commits(root):
    log = git(root, "log", "--all", "--format=%H%x1f%an <%ae> %cn <%ce>%x1f%B%x1e") or ""
    for record in log.split(RECORD):
        sha, _, rest = record.strip().partition(FIELD)
        people, _, body = rest.partition(FIELD)
        if sha:
            yield sha[:12], people, body


def _history(root):
    commits = list(_commits(root))
    signed = [sha for sha, _, body in commits if SIGNED.search(body)]
    bots = [sha for sha, people, _ in commits if BOT.search(people)]
    findings = []
    if signed:
        pushed = [sha for sha in signed if (git(root, "branch", "-r", "--contains", sha) or "").strip()]
        proof = f"{len(pushed)} already pushed" + (f": {', '.join(pushed[:SHOWN])}" if pushed else "")
        findings.append({"rule": RULE, "file": ".git", "line": 0, "cap": ATTRIBUTION, "proof": proof,
                         "what": f"{len(signed)} commits carry an AI tool attribution: {', '.join(signed[:SHOWN])}"})
    if bots:
        findings.append({"rule": RULE, "file": ".git", "line": 0, "proof": "author and committer, never rewritten",
                         "what": f"{len(bots)} commits made by an AI bot identity: {', '.join(bots[:SHOWN])}"})
    refs = (git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes") or "").split()
    named = [ref for ref in refs if AI_BRANCH.search(ref)]
    if named:
        findings.append({"rule": RULE, "file": ".git", "line": 0, "proof": "git for-each-ref",
                         "what": f"branches named after an AI tool: {', '.join(named[:SHOWN])}"})
    return findings


def _runs_agent(root, rel):
    try:
        return bool(AI_ACTION.search((root / rel).read_text(encoding=ENCODING, errors=DECODE_ERRORS)))
    except OSError:
        return False


def _tracked(root):
    listed = (git(root, "ls-files") or "").splitlines()
    findings = []
    for rel in listed:
        if WORKFLOW.search(rel) and _runs_agent(root, rel):
            findings.append({"rule": RULE, "file": rel, "line": 0, "cap": ATTRIBUTION,
                             "what": "workflow running an AI agent", "proof": LISTED_BY})
        elif AI_TRACKED.search(rel):
            findings.append({"rule": RULE, "file": rel, "line": 0, "what": "AI tooling file tracked by git",
                             "proof": LISTED_BY})
        elif ENV_FILE.search(rel) and not rel.endswith(ENV_SAMPLES):
            findings.append({"rule": 0, "file": rel, "line": 0, "cap": "secret", "points": 0,
                             "what": "environment file tracked by git", "proof": LISTED_BY})
    return findings, len(listed)


def check(files, root, config):
    if git(root, REV_PARSE, "--is-inside-work-tree") is None:
        return [], {"git": False}
    findings, tracked = _tracked(root)
    findings += _history(root)
    branch = (git(root, REV_PARSE, "--abbrev-ref", "HEAD") or "").strip()
    dirty = sorted(line[3:] for line in (git(root, "status", "--porcelain") or "").splitlines())
    return findings, {"git": True, "branch": branch, "tracked_files": tracked, "dirty_files": dirty}
