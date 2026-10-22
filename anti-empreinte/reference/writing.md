# Prose

For everything a person reads: README, documentation, article, web page text, letter, commit message,
pull request body, and your own replies. `scan.py` sees characters, words and markdown shapes; the
structures and the rhythm below only show up when you read.

## Typography

Never an em dash (U+2014) or a horizontal bar (U+2015): use a comma, a colon, parentheses or two
sentences. Never curly quotes or a curly apostrophe: straight `"` and `'` only. In French, no `« »`
and no no-break space before `: ; ? !`, an ordinary space instead.

No invisible character: no-break space U+00A0, narrow no-break space U+202F, thin and other fixed
spaces U+2002 to U+200A, zero width space U+200B, joiners U+200C and U+200D, word joiner U+2060,
byte order mark U+FEFF inside a file, soft hyphen U+00AD, direction marks U+200E, U+200F and
U+202A to U+202E, the Tag block U+E0000 to U+E007F, variation selectors U+FE00 to U+FE0F and
U+E0100 to U+E01EF. Private Use Area characters (U+E000 to U+F8FF) in prose are chatbot citation
wrappers. OpenAI confirmed in April 2025 that two of its models produced U+202F by accident; tag
characters are a known channel for hidden instructions. All of them go.

No emoji anywhere: heading, bullet, table cell, console output, README, commit, message.

## Formatting

Markdown shapes give a text away before anyone reads it.

- No `---` rule between sections, in markdown or as `<hr>`, nor a WordPress separator block
  (`wp:separator`, `wp-block-separator`). Headings separate sections. A `---` stays only where it is
  syntax: front matter, a setext heading underline, a table.
- Headings in sentence case, never Title Case. Never skip a heading level.
- Never a list right under a heading: one sentence first, or no list. Never a list where two sentences
  do the job. Never a table for data that is not tabular.
- Bold marks a defined term, never an idea to stress. Never bullets that open on a bold lead-in
  (`- **Term**: explanation`).
- Never `> [!NOTE]` or `> [!WARNING]` callouts by reflex.
- A nested fenced block needs a longer outer fence: four backticks around three. The reverse is a
  known model signature, and it breaks the page.
- No closing recap. No paragraphs all calibrated to the same size. A structure with no flaw at all is a
  marker in itself.

## Words

English words to avoid: delve, tapestry, landscape used figuratively, testament, vibrant, pivotal,
crucial, intricate, intricacies, meticulous, bolster, garner, underscore, interplay, multifaceted,
nuanced, foster, leverage, utilize, commence, facilitate, encompass, paramount, groundbreaking,
cutting-edge, game-changer, transformative, seamless, robust, comprehensive, aforementioned,
harnessing, spearheading, showcasing, highlighting, emphasizing, enhancing, unprecedented,
remarkable, profound, boasts, nestled, streamline, realm, synergy, ever-evolving, embark, elevate,
empower, unlock, unleash, invaluable, noteworthy, resonate, bustling, beacon, enduring, deep dive,
unpack, navigate used figuratively, lean into, double down, circle back, move the needle, stands as,
serves as, plays a vital role, it's worth noting.

The words that spread in 2026 are ordinary on their own and only count in clusters: challenge,
clearer, dependable, echoed, matters, practical, prioritize, quietly, steady, universally. They are
not in the script; notice them when three show up in one paragraph.

French words to avoid: crucial, essentiel, indispensable, fondamental, captivant, vibrant, par
ailleurs, ainsi, néanmoins, notamment, en outre, véritable, incontournable, au cœur de, un large
éventail, pierre angulaire, témoigne de, joue un rôle clé, force est de constater, il convient de,
plongeons, en somme, en définitive, n'hésitez pas, "dans le paysage actuel", "il est important de
noter".

## Openings, closings, emphasis

Never open on: Certainly, Absolutely, Sure, Great question, I'd be happy to, However, Moreover,
Furthermore, Additionally, Interestingly, Notably, Importantly, Indeed, Overall, De plus, En
conclusion.

Never write: "Here's the thing", "The real X is", "The truth is", "Let me be clear", "In today's X",
"In a world where", "It turns out", "Without further ado", "Full stop", "Period", "Let that sink in",
"Make no mistake", "This matters because", "In conclusion", "At the end of the day", "I hope this
helps", "Let me know if you need anything else", "You're absolutely right", "Perfect", "Excellent",
"That's a great question".

## Structures

These sentence shapes come back in model output whatever the topic.

- No negative parallelism: "not just X, it's Y", "not only X but also Y", "X rather than Y", "ce
  n'est pas X, c'est Y", "non seulement".
- No lists of three by reflex: two items or four.
- Never open on a negation: say what the thing is.
- No vague attribution ("studies show", "experts agree"), no false range ("from X to Y"), no inflated
  stakes ("marks a turning point", "a pivotal moment"), no participle tacked on for depth ("...,
  highlighting its importance").
- Use the verb to be: "X is Y", never "X serves as Y" or "X stands as Y".
- No fragments for effect ("X. Full stop."), no negative enumeration ("Not an X. Not a Y. A Z."), no
  rhetorical question answered at once.
- No fictional agency (decisions do not emerge, culture does not shift by itself), no disembodied
  narrator ("people tend to").
- No reflex hedging (almost, rather, tends to, to some extent), no empty adverb (really, simply,
  literally, honestly, fundamentally), no lazy absolute (always, never, everything, every).
- Never rank or announce your own arguments. Never invent a metaphor the reader must decode.
- Outlines that end on "Challenges" then "Future outlook", and padding such as "independent coverage"
  or a reminder of how sources should be read, are 2026 chatbot habits.
- Jargon to avoid: "load bearing", "hand-waving", "honest framing", "worth stating plainly", "here's
  where I'd push back".

## Rhythm

Mix short and long sentences, and paragraphs of different sizes. Regular lengths are the most reliable
statistical tell, ahead of any word. Read the text aloud in your head: three sentences in a row of the
same shape get rewritten.

## Residue from chat apps

Text pasted from a chatbot carries its plumbing. Remove it and the link parameters: ChatGPT
`oaicite`, `contentReference[...]`, `turn0search0` and other `turnNsearchN`, `citeturn`,
`utm_source=chatgpt.com` or `utm_source=openai` in links; Gemini `[cite: 1]` and
`[span_1](start_span)`; Grok `grok_card`; DeepSeek `【85†L261-269】`; Perplexity `[web:1]`; the
`:::writing{...}` wrapper. Also `<think>`, `Thought:`, "let's think step by step", "As an AI language
model", any mention of a knowledge cutoff, any fragment of a prompt.

## Letters and applications

Never "I am writing to express my strong interest in", "I wanted to reach out", nor vague praise of a
company's culture without naming a product.

## Sources

Never write a reference, a DOI, an ISBN, a page number or a URL you have not checked. A fabricated
citation cannot be taken back once published. When in doubt, say the source was not checked.

## Translation

Never copy the structure of the source language. A translation shows through rigid sentences and
literal word choices, more than through vocabulary.

## README and documentation

No emoji in the title, no row of shields.io badges, no table of contents on a short page, no stock
outline (Overview, Features, Tech stack, Installation, Usage, Contributing, License, Contact).

## Commit messages and pull requests

Follow the repository's history: its language, its form, its own types. Never apply conventional
commits by reflex when the repository does not. Vary the length. The pull request uses the
repository's template or prose. The attribution rules are in `git.md`.
