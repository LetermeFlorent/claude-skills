# Model tells

Each model family has defaults that give it away even when every banned word is gone. Read the part
for the model you are, then the other one: text often passes through both. These are tendencies seen
across the family, not version-specific facts; a tell that a newer version dropped costs nothing to
avoid.

## Your own habits first

Whatever model you are, you reach for the same moves under pressure: the same opener, the same three
bullets, the same closing offer, the same sentence length. Before handing over, reread as a stranger
looking for your signature. A sentence that came out the way you always write it gets rewritten, not
reworded. When unsure whether a phrase is one of yours, assume it is.

## Claude (Opus, Sonnet, Haiku, 4.x to 5.5)

Words and phrases:

- "genuinely", "honestly", "actually" as intensifiers; "the honest answer", "to be clear", "worth
  flagging", "worth noting", "it's worth", "the catch is", "the key insight", "the real question".
- "load-bearing", "hand-wavy", "first-class", "footgun", "under the hood", "in practice",
  "concretely", "a few things", "a couple of options".
- Agreement and praise: "You're right", "Good catch", "Great catch", "Fair point", "You're right to
  push back", "That makes sense".
- Narrating the work: "Let me", "I'll", "Now I'll", "Here's what I found", "Here's what's
  happening", "Short answer:", "TL;DR".
- Closing offers: "Want me to...?", "Should I...?", "Let me know if...", "Happy to...".

Shapes:

- The colon reveal ("Here's the problem: ..."), and a bold label opening each bullet.
- "It's not X, it's Y" and "X, not Y" contrasts; three-item lists; a one-line summary bolded at the
  top, then the same thing again at the bottom.
- Headings like "Root cause", "What changed", "Why this works", "Next steps", "Summary".
- Parenthetical asides in every other sentence; hedges stacked ("probably", "likely", "should").
- Answers that restate the question before answering it.
- Haiku: shorter, more lists and headers for small answers. Opus: longer sentences, more qualifiers,
  more nested structure. Sonnet sits between.

In code:

- A docstring on every function, comments that narrate the next line, section banners
  (`# --- Helpers ---`), `# Example usage` blocks under `if __name__ == "__main__":`.
- Defensive checks for cases that cannot happen, broad `try/except` that prints and continues.
- Status prints with check marks or "Done!", progress messages in a CLI that did not need them.
- Test names that read as sentences (`test_should_return_empty_list_when_input_is_empty`) and one
  assertion per test by reflex.
- README skeleton: Overview, Features, Installation, Usage, Configuration, Contributing, License.

## Qwen (Qwen 3 family: 3, 3.5, 3.6, 3.8 and later)

Words and phrases:

- Openers: "Certainly!", "Sure!", "Of course!", "Great question!", "Okay, so", "Alright,".
- Closers: "I hope this helps!", "Feel free to ask", "Let me know if you have any other
  questions", "In summary,", "In conclusion,".
- Reasoning that leaks into the answer: "Wait,", "Hmm,", "Let me think", "Let me double-check",
  "Okay, let me verify", "But wait".
- Calques from Chinese: "As follows:", "The specific steps are as follows", "It should be noted
  that", "In addition,", "Firstly, ... Secondly, ... Finally,", "comprehensive", "effectively",
  "relevant" used as filler.

Shapes:

- `### 1. **Title**` numbered bold headings, emoji in headings (check marks, pins, rockets,
  magnifiers), `---` between every section, a table even for two rows.
- Bold "Key points:", "Note:", "Tips:" blocks, and a closing "Summary" section repeating the answer.
- Uniform paragraphs of the same length, each starting with a transition word.

Leaks specific to Qwen:

- `<think>` and `</think>`, often an empty `<think>\n\n</think>` pair at the top of the answer.
- `/think` and `/no_think` switches copied into the text.
- Chat template tokens: `<|im_start|>`, `<|im_end|>`, `<|endoftext|>`.
- Full-width punctuation next to Latin letters (`，`, `。`, `：`, `（`, `）`), Chinese characters in
  the middle of English or French text, Chinese code comments (`# 示例`, `# 注意`).

In code:

- Type hints and docstrings on everything, Chinese or English comments explaining each step,
  `print("Result:", result)` demos at the end, `main()` wrappers around three lines.

## Checking

`scan.py` catches the leaks (template tokens, think tags, full-width punctuation next to Latin
letters) and the stock phrases it knows. Rhythm, structure and your own habits only show when you read
the text again as someone else would.
