---
name: claude-model-effort
description: Use when the user types /claude-model-effort, when about to start a subagent or a workflow agent on a Claude model (Claude Code, OpenCode with Claude) and its model or effort level must be picked, when a task seems to need a stronger or a cheaper model, or when a run is about to use the max effort level.
---

# Picking a Claude model and an effort level

This skill and the other-model-effort skill are the only ones in the repository that name models and effort
levels. Every other skill leaves them out, so the choice is made here, once, for each agent you start. The
tables below also serve other-model-effort, which maps them onto models that are not Claude.

Each task type has a minimum (the cheapest setting that does the job) and a ceiling. Anything between the
two is a valid choice; start at the minimum and climb only when a run comes back wrong or stops short.
The goal is the best result for the fewest tokens.

## Rules

These hold for every agent, whatever the task.

1. Never the `max` effort level. The ceiling in the table is already the upper bound; nothing goes above it.
2. The effort level sets the depth of reasoning, not the quality of the model. The five levels are `low`,
   `medium`, `high`, `xhigh`, `max`. `medium` is the everyday default; `xhigh` is kept for long agentic
   runs and decisions that cost a lot when wrong.
3. Set the model and the effort on the agent call itself (Claude Code: the `model` and `effort`
   parameters of the Agent tool, or the `model` and `effort` keys of an agent file's front matter).
4. When the user or a project's instructions name a model or an effort for a task, theirs wins.
5. Several task types in one agent: take the highest minimum among them.
6. A task that fails twice at one setting moves up one step (effort first, then model), never past the
   ceiling. Past the ceiling, the task needs splitting, not a bigger model.

Models, lightest first: Haiku 5.5 (fast and cheap), Sonnet 5.5 (all-round), Opus 5.5 (deep reasoning).

## Research and reading

Mostly reading, little reasoning.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Web research: docs, watch, comparing sources | Haiku low | Sonnet low | Haiku summarises a page; crossing several sources needs Sonnet low, no higher. |
| File or folder search: glob, grep, locate | Haiku low | Haiku medium | Mechanical; medium keeps it from stopping early or skipping a check. |
| File reader: a doc, a PDF, summing up existing code | Haiku low | Haiku high | Pulling one fact is low; a long document is high, still no Sonnet. |
| Image reader: OCR, a screenshot, a chart | Haiku low | Haiku high | Readable text is low; describing a layout is high, still no Sonnet. |
| Logs or a stack trace | Haiku medium | Sonnet medium | Lots of reading, little reasoning; Sonnet once the cause must be traced. |

## Code and development

The core of the work.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Everyday code: a function, a component, a simple fix | Sonnet low | Sonnet medium | Low for well-framed work, medium is the real working default. |
| Script writer: short bash or Python, throwaway automation | Haiku medium | Sonnet medium | Haiku low forgets edge cases. |
| Running tests, reading the failure, fixing | Sonnet medium | Opus medium | A failing test means tracing a cause; Opus avoids fix loops. |
| Browser test: chrome-bidi, screenshots, responsive | Sonnet medium | Opus medium | Seeing the gap between expected and shown is visual reasoning. |
| Git and commits: message, diff summary, simple conflict | Haiku low | Haiku medium | No deep reasoning; the best place to save tokens. |
| Technical writing: README, API explanations | Haiku medium | Sonnet medium | Sonnet keeps tone and consistency over a long document. |
| Code review: a PR, traps and gaps | Sonnet medium | Opus medium | Spotting what is missing is harder than fixing. |
| Multi-file refactor: rename, move, spread an API | Sonnet medium | Opus medium | Lots of context to keep consistent. |
| Regular expressions | Sonnet medium | Opus medium | Short but tricky; a wrong regex passes simple tests. |
| SQL: joins, aggregates, a slow query | Sonnet medium | Opus medium | A badly thought join costs hours of database time. |
| Docker and CI/CD: Dockerfile, pipeline, deploy script | Sonnet medium | Opus medium | Errors only show at deploy time, often in production. |
| External API integration: auth and errors | Sonnet medium | Opus medium | The error cases are the real work. |
| Rust systems code: borrows, lifetimes, concurrency | Sonnet medium | Opus high | The compiler guides simple errors; the rest shows only in use. |
| Database migrations: Prisma, SQL, schema changes | Sonnet medium | Opus high | Passes locally, breaks in production; rollback costs more than tokens. |
| Teams app and Microsoft SDK: host, permissions | Sonnet medium | Opus medium | Little code, many unforgiving host and permission rules. |

## Code optimisation

Opus is the floor here: Sonnet does not hold enough context to see what a rewrite breaks elsewhere.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Rewriting for readability, structure or speed | Opus medium | Opus high | Medium for an isolated file, high once the area is shared. |
| Technical debt: dead code, duplication, useless dependencies | Opus medium | Opus high | Removing what looks unused is how a quiet feature breaks. |

## Specialised and visual

Visual and spatial work needs a high floor.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| 3D model: scene, materials, geometry, export | Opus high | Opus xhigh | Below that, spatial consistency goes; xhigh is the working setting. |
| Shaders and GPU rendering: WGSL, wgpu, textures | Opus high | Opus xhigh | A wrong shader does not crash, it shows something almost right. |
| Design and UI: mock-up, hierarchy, palette | Sonnet medium | Opus medium | Several constraints held at once. |
| Accessibility: contrast, keyboard, screen readers | Sonnet medium | Opus medium | The gaps are invisible to the eye. |

## Large code and long jobs

Past a few files, a mistake costs far more than the tokens: the aim is not to redo the work three times.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Large feature: several files, API and UI together | Opus low | Opus medium | The plan matters more than typing speed. |
| Rewrite or migration: new framework, major version | Opus medium | Opus xhigh | The whole project map must be held. |
| Understanding an unknown codebase | Sonnet medium | Opus medium | Lots of context to assemble. |
| Mass test generation: a whole module | Sonnet medium | Opus medium | Finding the edge cases takes reasoning. |
| Long agentic task: hours, many steps, few human checks | Opus medium | Opus xhigh | Stopping early costs a full relaunch. |
| Performance and profiling | Opus medium | Opus xhigh | A fix for one case can break three others; measure first. |
| Architecture and stack choices | Opus medium | Opus xhigh | A bad decision here costs days. |
| Hard debugging: reproducible but not understood, regression | Opus medium | Opus xhigh | Cheaper than three failed attempts at a lower setting. |
| Security review: injection, hardcoded secrets, vulnerable dependencies | Opus medium | Opus xhigh | An audit that misses a flaw is worthless. |

## Data and content

Volume makes every token count.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Bulk processing: classify, extract, route hundreds of items | Haiku low | Haiku medium | Best value for volume. |
| Structured extraction: clean JSON from free text | Haiku low | Haiku medium | Form, not substance; medium avoids missing or invented fields. |
| Translation and i18n: language files, consistent tone | Haiku medium | Sonnet medium | Sonnet keeps the terminology of a whole file. |
| Excel and PDF generation: tables, formulas, layout | Sonnet medium | Opus medium | Real-world data is dirty and the layout is checked by eye. |

## /claude-model-effort <task>

Find the row that matches the task (several rows: rule 5), then answer in the user's language with the
minimum, the ceiling and the reason, in two or three lines. No row matches: take the closest one and say
which. Never answer `max`.
