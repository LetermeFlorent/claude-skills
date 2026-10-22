import re

from signatures import TRAILER

STRAIGHT = {0x2018: "'", 0x2019: "'", 0x201A: "'", 0x201B: "'", 0x2039: "'", 0x203A: "'",
            0x201C: '"', 0x201D: '"', 0x201E: '"', 0x201F: '"', 0x00AB: '"', 0x00BB: '"'}
INVISIBLE_POINTS = (0x00AD, 0x180E, 0x200B, 0x200C, 0x200D, 0x200E, 0x200F, (0x202A, 0x202E), (0x2060, 0x2064),
                    (0x2066, 0x2069), 0xFEFF, (0xFE00, 0xFE0F), (0xE000, 0xF8FF), (0xE0000, 0xE007F),
                    (0xE0100, 0xE01EF))
SPACE_POINTS = (0x00A0, 0x202F, (0x2002, 0x200A), 0x205F)
HAND_POINTS = (0x2014, 0x2015)
EMOJI_POINTS = ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF), 0x231A, 0x231B, (0x23E9, 0x23F3),
                (0x23F8, 0x23FA), 0x3030, 0x303D, 0x3297, 0x3299)


def _class(points):
    return "".join(chr(point) if isinstance(point, int) else f"{chr(point[0])}-{chr(point[1])}" for point in points)


def _words(items):
    return re.compile(r"\b(" + "|".join(items) + r")\b", re.IGNORECASE)


INVISIBLE = re.compile(f"[{_class(INVISIBLE_POINTS)}]")
SPACES = re.compile(f"[{_class(SPACE_POINTS)}]")
HAND_TYPOGRAPHY = re.compile(f"[{_class(HAND_POINTS)}]")
EMOJI = re.compile(f"[{_class(EMOJI_POINTS)}]")
CURLY = re.compile(f"[{_class(tuple(STRAIGHT))}]")
FRENCH_QUOTES = re.compile(r"\u00ab\s*(.*?)\s*\u00bb")

ENGLISH = ("delve[sd]?", "delving", "tapestry", "testament", "vibrant", "pivotal", "crucial", "intricate",
           "intricacies", "meticulous(ly)?", "bolster(s|ed)?", "garner(s|ed)?", "underscore[sd]?", "interplay",
           "multifaceted", "nuanced", "foster(s|ed|ing)?", "leverag(e|es|ed|ing)", "utiliz(e|es|ed|ing)",
           "commence[sd]?", "facilitat(e|es|ed|ing)", "encompass(es|ed|ing)?", "paramount", "groundbreaking",
           "cutting-edge", "game-chang(er|ing)", "transformative", "seamless(ly)?", "robust", "comprehensive",
           "aforementioned", "harness(es|ed|ing)?", "spearhead(s|ed|ing)?", "showcas(e|es|ed|ing)",
           "unprecedented", "remarkabl[ey]", "profound(ly)?", "boasts", "nestled", "streamlin(e|es|ed|ing)",
           "realm", "synergy", "deep dive", "unpack", "lean into", "double down", "circle back",
           "move the needle", "ever-evolving", "embark(s|ed|ing)?", "elevat(e|es|ed|ing)", "empower(s|ed|ing)?",
           "unlock(s|ed|ing)? the", "unleash(es|ed|ing)?", "invaluable", "noteworthy", "resonat(e|es|ed|ing)",
           "bustling", "beacon", "enduring", "stands as", "serves as a", "plays a (vital|key|pivotal) role",
           "in the realm of", "it'?s worth noting", "landscape of")
FRENCH = ("crucial(e|es|aux)?", "essentiel(le|les|s)?", "indispensables?", "fondamenta(l|le|les|ux)",
          "captivant(e|es|s)?", "vibrant(e|es|s)?", "par ailleurs", "ainsi", "néanmoins", "notamment",
          "dans le paysage actuel", "il est important de noter", "force est de constater", "il convient de",
          "plongeons", "en outre", "véritable", "incontournables?", "au cœur de", "un large éventail",
          "témoigne de", "joue un rôle (clé|majeur|central)", "pierre angulaire",
          "n'hésitez pas", "en somme", "en définitive")
VOCABULARY = _words(ENGLISH + FRENCH)
PHRASES = re.compile(
    r"^\s*(certainly|absolutely|sure|great question|i'?d be happy to|however|moreover|furthermore|additionally"
    r"|interestingly|notably|importantly|indeed|overall|in conclusion|en conclusion|de plus)\b"
    r"|here'?s the thing|the (real|truth) \w+ is|let me be clear|in today'?s|in a world where|it turns out"
    r"|without further ado|full stop|let that sink in|make no mistake|this matters because"
    r"|at the end of the day|i hope this helps|let me know if you need|you'?re absolutely right"
    r"|that'?s a great question|\bnot (just|only|merely) [^.]{1,60}\b(but|it'?s|it is)\b"
    r"|\bce n'est pas [^.]{1,60}, c'est\b|\bnon seulement\b|\bpas seulement [^.]{1,60}\bmais\b",
    re.IGNORECASE)
PLACEHOLDER = re.compile(r"\.\.\.\s*(existing|rest of( the)?) code\s*\.\.\.|TODO:?\s*implement|Example usage|"
                         r"your[-_]api[-_]key[-_]here|replace with your|\[insert [^\]]+\]", re.IGNORECASE)
RESIDUE = re.compile(r"</?think>|^\s*(Thought|Step \d+):|let'?s think step by step|as an ai( language model)?\b"
                     r"|as of my (last )?(knowledge|training) (cutoff|update)|oaicite|contentReference\["
                     r"|\bturn\d+(search|view|news|image|fetch)\d+|utm_source=(chatgpt\.com|openai)|\bciteturn"
                     r"|\[cite:\s*\d+|\[span_\d+\]\(start_span\)|grok_card|【\d+†|\[web:\d+\]"
                     r"|:::writing\{", re.IGNORECASE)
SIGNATURE = re.compile(TRAILER.pattern + r"|made with cursor|pr created automatically by jules"
                       r"|link to devin session", re.IGNORECASE | re.MULTILINE)
UI_DEFAULT = re.compile(r"font-family:[^;]*\b(Inter|Space Grotesk|Geist|Instrument Serif)\b|['\"](Inter|Geist)['\"]"
                        r"|\bindigo-\d{3}\b|#6366f1|#8b5cf6|#a855f7|#4f46e5|backdrop-filter|from-indigo"
                        r"|to-purple-|to-violet-|bg-clip-text", re.IGNORECASE)
