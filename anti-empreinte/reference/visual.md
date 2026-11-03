# Interfaces and pages

Pick a palette, a font and a grid before the first component, or ask. The project's own theme wins over this page.

## Defaults nobody chose

Banned unless the user names them:

- the Inter font, and its 2026 replacements Space Grotesk, Geist, and Instrument Serif headings over a sans body;
- the indigo to violet gradient, `indigo-500`, `#6366f1`, `#4f46e5`, `#8b5cf6`, `#a855f7`, the stock Tailwind palette, gradient text via `bg-clip-text`;
- glassmorphism (`backdrop-filter`), blurred orbs behind a hero;
- three rounded cards in a row, three icon feature blocks, a hero with a badge above the title and two buttons below;
- one soft shadow and one large radius on everything;
- dark mode by reflex (slate background, neon accent);
- icons as decoration, one per heading;
- a three-tier pricing table with the middle one highlighted, a testimonial carousel, a stats row with invented numbers.

`scan.py` reports fonts, colours, `backdrop-filter` and gradient classes in page and style files; layouts only show by looking at the page.

## Instead

Start from what the page must say, to whom, in what order. One justified typeface, one accent. Vary section rhythm (full-width band, two columns, list, plain text). Real copy, real numbers, real photographs or none. No `<hr>` or WordPress separator block between sections; a border belonging to a card, header, footer or table is layout and stays.
