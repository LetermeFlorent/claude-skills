---
description: Drive Chrome, or Firefox on request, for a page task, or capture a page at phone and desktop widths and measure every image.
argument-hint: "<url or local folder> [widths, 390,1440 by default] | <what to do on a page>"
allowed-tools: Read,Bash,Skill
---

Arguments: $ARGUMENTS. Empty: ask for the address.

Load `browser-bidi` skill. Url or local folder alone, optional widths: run its `/browser-bidi` visual test; anything else: page task done with its scripts. Pick window mode yourself. No commit. Answer in user's language, few lines: what breaks at which width, images to redo, captures folder, or task result.
