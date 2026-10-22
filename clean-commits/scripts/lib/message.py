import re

from history import CONVENTIONAL, language

MAX_SUBJECT = 72
MAX_LINE = 100
TYPES = {"feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"}
AI_EMAILS = (r"noreply@anthropic\.com|noreply@openai\.com|cursoragent@cursor\.com|copilot@users\.noreply\.github\.com"
             r"|copilot-swe-agent|devin-ai-integration|google-labs-jules|gemini-code-assist|claude\[bot\]")
AI_MODELS = r"claude[ -](code|opus|sonnet|haiku|fable|\d)|chatgpt|gpt-?\d|codex|copilot|cursor( agent)?\b|gemini"
ATTRIBUTION = re.compile(
    rf"^\s*(co-authored-by|co-developed-by|assisted-by|generated-by)\s*:.*({AI_EMAILS}|{AI_MODELS}|anthropic|openai)"
    r"|^\s*claude-[\w-]+\s*:|^\s*made[- ]with\s*:?\s*cursor|^\s*agent-logs-url\s*:"
    r"|generated (with|by) \[?(claude|codex|copilot|cursor|gemini|chatgpt|devin|jules|aider)"
    r"|claude\.ai/code|claude\.com/claude-code|chatgpt\.com/codex"
    rf"|{AI_EMAILS}", re.IGNORECASE | re.MULTILINE)
EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF), (0xFE00, 0xFE0F), (0x200D, 0x200D),
                (0xE0000, 0xE007F))
TYPOGRAPHY_POINTS = (0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x00AB, 0x00BB, 0x00A0, 0x202F, 0x2009, 0x200B,
                     0x00AD, 0xFEFF)
EMOJI = re.compile("[" + "".join(f"{chr(low)}-{chr(high)}" for low, high in EMOJI_RANGES) + "]")
TYPOGRAPHY = re.compile("[" + "".join(map(chr, TYPOGRAPHY_POINTS)) + "]")
TRAILING = (".", " ")


def _form(subject, found):
    if not found["conventional"]:
        return []
    match = CONVENTIONAL.match(subject)
    allowed = TYPES | set(found["types"])
    if not match:
        return ["the history uses type(scope): subject, this subject does not"]
    if match.group("type") not in allowed:
        known = ", ".join(sorted(allowed))
        return [f"type {match.group('type')} is neither standard nor used in this history: {known}"]
    return []


def _subject(subject, found, wanted):
    problems = [] if len(subject) <= MAX_SUBJECT else [f"subject is {len(subject)} characters, {MAX_SUBJECT} at most"]
    problems += ["subject ends with a period or a space"] if subject.endswith(TRAILING) else []
    read_as = language(subject)
    if wanted and read_as and read_as != wanted:
        problems.append(f"subject reads as {read_as}, the messages here are in {wanted}")
    return problems + _form(subject, found)


def check(text, found, wanted):
    lines = text.strip("\n").splitlines()
    if not lines or not lines[0].strip():
        return ["empty message"]
    problems = _subject(lines[0], found, wanted)
    if len(lines) > 1 and lines[1].strip():
        problems.append("a blank line must separate the subject from the body")
    problems += [f"line {number} is over {MAX_LINE} characters" for number, line in enumerate(lines, 1)
                 if len(line) > MAX_LINE]
    if ATTRIBUTION.search(text):
        problems.append("AI tool attribution: remove the line")
    if EMOJI.search(text):
        problems.append("emoji in the message")
    if TYPOGRAPHY.search(text):
        problems.append("em dash, curly quote, guillemet or invisible space: use plain ASCII punctuation")
    return problems
