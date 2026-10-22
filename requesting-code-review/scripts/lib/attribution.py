import re

AI_EMAILS = (r"noreply@anthropic\.com|noreply@openai\.com|cursoragent@cursor\.com"
             r"|copilot@users\.noreply\.github\.com|copilot-swe-agent|devin-ai-integration"
             r"|google-labs-jules|gemini-code-assist|claude\[bot\]")
AI_MODELS = r"claude[ -](code|opus|sonnet|haiku|fable|\d)|chatgpt|gpt-?\d|codex|copilot|cursor( agent)?\b|gemini"
TRAILER = re.compile(
    rf"^\s*(co-authored-by|co-developed-by|assisted-by|generated-by)\s*:.*({AI_EMAILS}|{AI_MODELS}|anthropic|openai)"
    r"|^\s*claude-[\w-]+\s*:|^\s*made[- ]with\s*:?\s*cursor|^\s*agent-logs-url\s*:"
    r"|generated (with|by) \[?(claude|codex|copilot|cursor|gemini|chatgpt|devin|jules|aider)"
    r"|claude\.ai/code|claude\.com/claude-code|chatgpt\.com/codex"
    rf"|{AI_EMAILS}", re.IGNORECASE | re.MULTILINE)
BOT_NAME = re.compile(r"\[bot\]$|\(aider\)$|^cursor agent$", re.IGNORECASE)
BAD_PREFIXES = ("claude/", "codex/", "copilot/", "cursor/", "devin/")


def message_hits(text):
    return [line.strip() for line in text.splitlines() if TRAILER.search(line)]


def author_hit(name):
    return bool(BOT_NAME.search(name.strip()))


def branch_hit(name):
    return name.startswith(BAD_PREFIXES)


def findings(commits):
    rows = []
    for commit in commits:
        short = commit["sha"][:7]
        rows += [f"{short} message: {line}" for line in message_hits(commit["body"])]
        for role in ("author", "committer"):
            if author_hit(commit[role]):
                rows.append(f"{short} {role}: {commit[role]}")
    return rows
