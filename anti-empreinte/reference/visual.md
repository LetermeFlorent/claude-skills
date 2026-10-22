# Interfaces and pages

A generated interface is recognised before a word is read: the same font, the same purple gradient, the
same three cards. Choose, or ask for, a palette, a font and a grid before the first component. When the
project already has a theme, it wins over this page.

## Defaults nobody chose

These are banned unless the user asks for them by name:

- the Inter font, and the second wave that replaced it in 2026: Space Grotesk, Geist, Instrument Serif
  for headings over a sans body;
- the indigo to violet or purple gradient, `indigo-500`, `#6366f1`, `#4f46e5`, `#8b5cf6`, `#a855f7`,
  the stock Tailwind palette, gradient text through `bg-clip-text`;
- glassmorphism through `backdrop-filter`, blurred orbs floating behind a hero;
- three rounded cards in a row, three feature blocks with an icon in a grid, a hero with a badge above
  the title and two buttons below;
- the same soft shadow and the same large radius on everything;
- dark mode by reflex, with a slate background and a neon accent;
- icon libraries used for decoration, one icon per heading;
- a pricing table of three tiers with the middle one highlighted, a testimonial carousel, a stats row
  ("10k+ users") with invented numbers.

`scan.py` reports the fonts, colours, `backdrop-filter` and gradient classes in page and style files.
The layouts only show when you look at the page.

## What to do instead

Start from the content and the brand: what the page must say, to whom, in what order. Pick one typeface
the project can justify and a palette with one accent. Vary the rhythm of sections: a full-width band, a
two-column block, a list, plain text. Real copy, real numbers, real photographs or none.

## Section separators on the web

No `<hr>` between sections, no WordPress separator block (`wp:separator`, `wp-block-separator`), no
decorative line drawn between two parts of an article. A border that belongs to a component (a card, a
header, a footer, a table) is layout and stays.
