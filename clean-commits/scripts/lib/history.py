import re
from collections import Counter

from repo import read

SAMPLE = 40
SHOWN = 5
MOST = 6
CONVENTIONAL_SHARE = 0.5
CONVENTIONAL = re.compile(r"^(?P<type>[a-z]+)(\((?P<scope>[^)]+)\))?!?: \S")
WORD = re.compile(r"[a-zà-ÿ]+")
ACCENT = re.compile(r"[àâçéèêëîïôûùüÿœ]")
FRENCH = {"le", "la", "les", "des", "du", "de", "un", "une", "et", "pour", "dans", "sur", "avec", "sans", "au", "aux",
          "ajout", "ajoute", "ajouter", "correction", "corrige", "corriger", "mise", "jour", "nouveau", "nouvelle",
          "suppression", "supprime", "premiere", "version", "nettoyage", "renomme", "deplace", "ne", "plus", "pas"}
ENGLISH = {"the", "a", "an", "add", "adds", "added", "fix", "fixes", "fixed", "for", "to", "of", "with", "remove",
           "update", "in", "on", "and", "from", "use", "make", "move", "rename", "drop", "support", "when", "into",
           "first", "version", "cleanup", "set", "bump", "initial", "refactor", "is", "not", "no"}
LANGUAGES = ("fr", "en")
FR, EN = LANGUAGES


def language(text):
    lowered = text.lower()
    words = WORD.findall(CONVENTIONAL.sub("", lowered))
    french = sum(word in FRENCH for word in words) + len(ACCENT.findall(lowered))
    english = sum(word in ENGLISH for word in words)
    if french == english:
        return None
    return FR if french > english else EN


def profile(root):
    output = read(root, "log", f"-{SAMPLE}", "--no-merges", "--format=%s") or ""
    subjects = [line for line in output.splitlines() if line.strip()]
    votes = Counter(filter(None, map(language, subjects)))
    matches = [found for found in map(CONVENTIONAL.match, subjects) if found]
    conventional = bool(subjects) and len(matches) / len(subjects) >= CONVENTIONAL_SHARE
    return {"commits": len(subjects), "language": votes.most_common(1)[0][0] if votes else None,
            "conventional": conventional, "types": Counter(found.group("type") for found in matches),
            "scopes": Counter(found.group("scope") for found in matches if found.group("scope")),
            "examples": subjects[:SHOWN]}


def describe(found):
    if not found["commits"]:
        return "no commit yet: ask the user the language of the messages"
    style = "conventional" if found["conventional"] else "free form"
    lines = [f"{found['language'] or 'unknown language'}, {style}, from the last {found['commits']} commits"]
    if found["conventional"]:
        lines.append("types: " + ", ".join(f"{name} {count}" for name, count in found["types"].most_common(MOST)))
        lines.append("scopes: " + (", ".join(name for name, _ in found["scopes"].most_common(MOST)) or "none"))
    lines += [f"  {subject}" for subject in found["examples"]]
    return "\n".join(lines)
