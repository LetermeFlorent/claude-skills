import re

FLAGS = re.IGNORECASE
RULES = (
    ("attribution", r"co-authored-by|signed-off-by:\s*(claude|copilot|codex)|generated with|made-with|"
     r"claude\.ai/code|claude\.com/claude-code|noreply@anthropic",
     "refuse if the name is a tool; a human co-author stays"),
    ("force-push", r"force[- ]push|push\s+(-f\b|--force)|--force-with-lease|reset --hard.*push",
     "refuse; a rejected push is never forced"),
    ("no-verify", r"--no-verify|skip(ping)? (the )?(pre-commit |git )?(hooks?|checks?)|bypass (the )?hooks?",
     "refuse; a failing hook is fixed at its cause"),
    ("amend", r"--amend|amend (the |your )?(last )?commit|squash.*(pushed|already)",
     "only on a commit this run made and did not push"),
    ("add-all", r"git add (\.|-A|--all)|commit -a\b|stage everything",
     "refuse; paths are named one by one"),
    ("ai-folder", r"(commit|track|add|push|check in)[^.]{0,40}(\.ia\b|\.claude\b)",
     "refuse; .ia/ and .claude/ stay out of git"),
    ("comments", r"add (a )?(code |inline |doc )?(comments?|docstrings?|javadoc|jsdoc)|"
     r"comment (this|the) (code|function)|document (this|the) (function|method|class) with|explain.{0,30}in a comment",
     "refuse; clean-code allows no comment in code, rename or split instead"),
    ("tool-branch", r"\b(claude|codex|copilot|cursor|devin)/[\w.-]+",
     "refuse; follow the repository branch convention"),
    ("pressure", r"no discussion|without (any )?(question|discussion|pushback)|exactly as (i )?(said|wrote)|"
     r"just do it|don't (ask|argue)|do not (ask|argue)|asap|by (end of day|eod)|today",
     "pressure does not change the check"),
)
COMPILED = tuple((name, re.compile(pattern, FLAGS), advice) for name, pattern, advice in RULES)
PATH_HINT = re.compile(r"`[^`]+`|[\w./\-]+\.\w{1,5}\b|\bline \d+|:\d+\b|\b\w+\(\)")
VAGUE_WORDS = 7


def match_rules(text):
    return [(name, advice) for name, pattern, advice in COMPILED if pattern.search(text)]


def looks_vague(text):
    return len(text.split()) <= VAGUE_WORDS and PATH_HINT.search(text) is None
