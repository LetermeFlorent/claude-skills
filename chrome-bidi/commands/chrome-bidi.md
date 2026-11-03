---
description: Drive Chrome for a page task, or capture a page at phone and desktop widths and measure every image.
argument-hint: "<url or local folder> [widths, 390,1440 by default] | <what to do on a page>"
allowed-tools: Read,Bash,Skill
---

Arguments: $ARGUMENTS. Empty: ask for the address.

Load the `chrome-bidi` skill. A url or local folder alone, with optional widths, runs its `/chrome-bidi` visual test; anything else is a page task done with its scripts. Pick the window mode yourself. No commit. Answer in the user's language, a few lines: what breaks at which width, images to redo, folder of the captures, or the result of the task.
