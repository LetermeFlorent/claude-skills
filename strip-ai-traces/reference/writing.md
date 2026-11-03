# Prose

For everything a person reads: README, docs, article, page text, letter, commit message, PR body. `scan.py` sees characters, words and markdown shapes; the structures and rhythm below only show up when you read.

## Typography

Never an em dash (U+2014) or horizontal bar (U+2015): use a comma, colon, parentheses or two sentences. Never curly quotes or apostrophes. In French no `« »` and no no-break space before `: ; ? !`.

Invisible characters that all go: U+00A0, U+202F, U+2002 to U+200A, U+200B, U+200C, U+200D, U+2060, U+FEFF inside a file, U+00AD, direction marks U+200E, U+200F, U+202A to U+202E, the Tag block U+E0000 to U+E007F, variation selectors U+FE00 to U+FE0F and U+E0100 to U+E01EF. Private Use Area characters (U+E000 to U+F8FF) in prose are chatbot citation wrappers.

## Formatting

Markdown shapes give a text away before it is read.

- A `---` stays only where it is syntax: front matter, setext underline, table.
- Never skip a heading level. Never a list where two sentences do the job, nor a table for data that is not tabular.
- Bold marks a defined term, never stress, never a bullet lead-in (`- **Term**: explanation`).
- No `> [!NOTE]` or `> [!WARNING]` callouts by reflex.
- A nested fenced block needs a longer outer fence: four backticks around three. The reverse breaks the page.
- No paragraphs all calibrated to the same size.

## Words

English to avoid: delve, tapestry, landscape (figurative), testament, vibrant, pivotal, crucial, intricate, intricacies, meticulous, bolster, garner, underscore, interplay, multifaceted, nuanced, foster, leverage, utilize, commence, facilitate, encompass, paramount, groundbreaking, cutting-edge, game-changer, transformative, seamless, robust, comprehensive, aforementioned, harnessing, spearheading, showcasing, highlighting, emphasizing, enhancing, unprecedented, remarkable, profound, boasts, nestled, streamline, realm, synergy, ever-evolving, embark, elevate, empower, unlock, unleash, invaluable, noteworthy, resonate, bustling, beacon, enduring, deep dive, unpack, navigate (figurative), lean into, double down, circle back, move the needle, stands as, serves as, plays a vital role, it's worth noting.

2026 words that only count in clusters of three in one paragraph (not in the script): challenge, clearer, dependable, echoed, matters, practical, prioritize, quietly, steady, universally.

French to avoid: crucial, essentiel, indispensable, fondamental, captivant, vibrant, par ailleurs, ainsi, néanmoins, notamment, en outre, véritable, incontournable, au cœur de, un large éventail, pierre angulaire, témoigne de, joue un rôle clé, force est de constater, il convient de, plongeons, en somme, en définitive, n'hésitez pas, "dans le paysage actuel", "il est important de noter".

## Openings, closings, stock phrases

Never open on: Certainly, Absolutely, Sure, Great question, I'd be happy to, However, Moreover, Furthermore, Additionally, Interestingly, Notably, Importantly, Indeed, Overall, De plus, En conclusion.

Never write: "Here's the thing", "The real X is", "The truth is", "Let me be clear", "In today's X", "In a world where", "It turns out", "Without further ado", "Full stop", "Let that sink in", "Make no mistake", "This matters because", "At the end of the day", "I hope this helps", "Let me know if you need anything else", "You're absolutely right", "Perfect", "Excellent", "That's a great question", "load bearing", "hand-waving", "honest framing", "worth stating plainly".

## Structures

These sentence shapes return whatever the topic.

- No negative parallelism ("not just X, it's Y", "not only X but also Y", "ce n'est pas X, c'est Y", "non seulement"), no opening on a negation, no "Not an X. Not a Y. A Z.".
- No list of three by reflex: two items or four.
- No vague attribution ("studies show"), false range ("from X to Y"), inflated stakes ("a pivotal moment"), participle tacked on for depth ("..., highlighting its importance").
- "X is Y", not "X serves as Y".
- No fragment for effect, no rhetorical question answered at once, no fictional agency ("decisions emerge"), no disembodied narrator ("people tend to").
- No reflex hedging (almost, rather, tends to), empty adverb (really, simply, literally, honestly, fundamentally) or lazy absolute (always, never, everything).
- Do not rank or announce your own arguments; do not invent a metaphor the reader must decode.
- No outline ending on "Challenges" then "Future outlook"; no padding about "independent coverage" or how sources should be read.

## Residue from chat apps

Remove it and the link parameters: ChatGPT `oaicite`, `contentReference[...]`, `turn0search0` and other `turnNsearchN`, `citeturn`, `utm_source=chatgpt.com` or `utm_source=openai`; Gemini `[cite: 1]`, `[span_1](start_span)`; Grok `grok_card`; DeepSeek `【85†L261-269】`; Perplexity `[web:1]`; the `:::writing{...}` wrapper. Also `<think>`, `Thought:`, "let's think step by step", "As an AI language model", any mention of a knowledge cutoff, any fragment of a prompt.

## By genre

Letters: never "I am writing to express my strong interest in", "I wanted to reach out", or praise of a company's culture without naming a product. Sources: never write a reference, DOI, ISBN, page number or URL you have not checked; say the source was not checked. Translation: do not copy the source language's structure. README: no emoji in the title, no shields.io badges, no table of contents on a short page, no stock outline (Overview, Features, Tech stack, Installation, Usage, Contributing, License, Contact). Commits and PRs: follow the repository's history, language and form, never Conventional Commits by reflex; attribution rules are in `git.md`.
