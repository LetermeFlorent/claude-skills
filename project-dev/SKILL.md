---
name: project-dev
description: Use when the user starts a project or types /projet, when they ask to build a site, an app, a game, a mod, a tool or a 3D model that does not exist yet, when mockups, screenshots, a palette, a logo or a site to imitate are named or sit in a folder, when a project with a spec or a plan in .ia/ is picked up again, or when a visible result is about to be called finished because its tests pass and its plan boxes are ticked.
---

# Running a project from the first idea to the finish

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

`/projet` takes a project through the skills that already exist, in a fixed order, with the user's
approval at three gates: the spec, the plan, the finish. It adds what none of them does on its own:
reference images. They are asked for at the start of every project, copied into the project,
described, handed to every agent that builds something visible, and compared with a capture of the
result before anything is called finished.

This file decides the order and the gates. How each step is done belongs to that step's skill: read
it when the step starts, from the folder next to this one (`<skill>/../<name>/SKILL.md`, `<skill>`
being this file's folder) or from `~/.claude/skills/<name>/SKILL.md`. A skill found in neither place
is done by hand from its line in the chain below, and the report says so. "Not installed" never
means the step is skipped.

`scripts/references.py` copies, lists and checks the images:
`python -I "<skill>/scripts/references.py" add|check ...`, forward slashes inside double quotes. It
never crashes; exit 2 is a refusal with its reasons, exit 1 a failure of git or of the tool.

## Rules that never bend

These hold whatever the hurry or the size, and breaking the letter of one breaks its spirit.

1. The first question of every project is "As-tu des images de référence ?": mockups, screenshots,
   a site or a game to imitate, a palette, a logo. It is asked even when the request names none,
   even for a tool with no screen, and before any colour, font or layout is chosen. Images named in
   the request are read first, and the question becomes "En as-tu d'autres ?".
2. Images live in `<project>/.ia/references/`, copied there by `references.py add`, never moved or
   edited at their source, each with its line in `references.md`. `.ia/` stays out of git and is
   never committed.
3. A spec comes before the plan and the plan before any product code, even for a small site and
   even when the user says to skip them. Under pressure they get shorter, never skipped.
4. Each gate is one `AskUserQuestion`, recommended answer first, on what the user can see: the spec
   path (brainstorming's own step 7 question is that gate, not a second one), the plan path and the
   finish options. A "go ahead" given before they saw it passes no gate. When they said they are away,
   take the recommended answer, say so in one line, and go on.
5. Every plan task that changes something visible names its images by absolute path with what to
   take from each, and its implementer opens them before writing code.
6. Something visible is not finished until a capture of it has been compared with each image that
   applies, and every difference has been fixed through the test-driven-development skill or
   accepted by the user. Green tests and ticked boxes are not that comparison.
7. Captures never touch the user's windows: a headless Chrome on the task's own port through the
   chrome-bidi skill, or the screenshot or render tool of a game or 3D editor when the session has one.
   What the run opened, it closes.

## The chain

Each step starts when the one before it is done. Code follows the clean-code skill, every file the
anti-empreinte skill, every commit the clean-commits skill.

| Step | Skill | What comes out | Gate |
|---|---|---|---|
| 1. Size and images | brainstorming for the size, this skill for the images | the size sentence, `.ia/references/` filled and checked | |
| 2. Grill and spec | brainstorming | `.ia/specs/<date>-<topic>-design.md` with its `## Références` section | spec |
| 3. Plan | writing-plans | `.ia/plans/<date>-<topic>.md`, images named per task, a last task that captures and compares | plan |
| 4. Isolation | using-git-worktrees | a worktree under `.ia/worktrees/`, its baseline read | |
| 5. Build | subagent-driven-development, test-driven-development inside each task, dispatching-parallel-agents for tasks sharing no file, systematic-debugging on any failure | commits on the branch | |
| 6. Comparison | this skill, with chrome-bidi or the game and 3D editor tools | each difference fixed or accepted | |
| 7. Verification and review | verification-before-completion, requesting-code-review, receiving-code-review | the suite read, the review applied | |
| 8. Finish | finishing-a-development-branch | merged, pull request, kept or dropped | finish |

A request that brainstorming sizes below "something that does not exist yet" is not a project: say
so in one line and follow brainstorming's own path. The image question still comes first when the
change shows on screen.

A worktree does not hold `.ia/`, which git does not track. Agents working in it read the spec, the
plan and the images from the main checkout, by absolute path.

## Picking a project up

Run with no argument inside a project, or with a project that has `.ia/`, the chain resumes where
the disk says it stopped.

| On disk | Next step |
|---|---|
| no `.ia/references/references.md` and no spec | 1, the image question first |
| references but no spec | 2 |
| a spec but no plan | 3 |
| a plan with unticked tasks | 5, from the first unticked task |
| every task ticked | 6, whatever the tests say |

## Reference images

Step 1 runs before the grill's other questions, because the answer settles many of them.

| The user gives | What to do |
|---|---|
| files or a folder | `references.py add "<project>" "<path>" ...` |
| a site or a page to imitate | a headless shot through chrome-bidi, saved in the temp folder, then `add` |
| a game, a model, an app | ask for a capture file; a named game place can use the game editor's screenshot tool |
| an image pasted in the chat | it has no file: describe it under a `## Sans fichier` heading of `references.md`, and ask for the file, which the comparison needs |
| nothing | one line in the spec's `## Références` section: "Aucune image de référence". Colours, font and layout then become questions of the grill, never defaults |

`add` creates the project folder when it does not exist yet, copies the images, skips what is not an
image and writes one `(à décrire)` line per new image. Then open every image and replace each
`(à décrire)` with what to take from it: colours with their hex code, layout, spacing, type, style;
and what not to take: placeholder text, a logo that is not the user's. `references.py check
"<project>"` refuses an image without its line, a line without its image, a file that is not an
image and a tracked `.ia/`. It prints the absolute paths that go into the spec and the plan. Run it
again after `git init`: it adds `.ia/` to the exclude file.

The spec's `## Références` section names every image with its line. In the plan, each visible task
carries a line in this shape, which `brief.py` of subagent-driven-development copies into the brief:

```text
Références : ouvrir C:/.../club-foot/.ia/references/accueil.png avant de coder ; reprendre le bandeau
vert #1b5e20, le logo rond à gauche, le bouton jaune #fbc02d à droite.
```

## Comparing before the finish

Step 6 runs on every project with references, after the last task and before verification.

1. Capture the result at the reference's width. A page: chrome-bidi headless on the task's own port, `nav` to the page
   (a `file:///` URL or the project's own server), `shot`, and `fullshot` when the reference is a full page. A game
   place: the screenshot tool of the game editor. A 3D model: the render tool of the 3D editor. Captures go to
   `<temp>/claude-skills/<project>-captures/` (`<temp>` is the system temp folder, `tempfile.gettempdir()`).
2. Open the capture, then the reference, and list each difference against what `references.md` says to take: a colour,
   a position, a missing or extra element, a size. Pixel-perfect is not the aim; what the line says to take is.
3. Each difference gets a test that fails on it, then the fix, through test-driven-development; or, when it is a
   matter of taste, one `AskUserQuestion` to keep it or fix it, fixing recommended. Capture again after the fixes.
4. Close the browser or the instance, delete the captures, and keep one line per image for the report: what matched,
   what was fixed, what the user accepted.

## Report

The answer to the user is in French and short: where the project stands in the chain, the images in
use, the answer at each gate passed, the comparison line per image, and the question of the next
gate asked before the last line.

## Files

`scripts/references.py` copies, lists and checks the reference images, with `scripts/lib/` for what it
shares. The unit tests run with `python -I -B -m unittest discover -s tests -p "test_*.py"` from this
folder. `commands/projet.md` is `/projet`, `LISEZMOI.md` the French notes.
