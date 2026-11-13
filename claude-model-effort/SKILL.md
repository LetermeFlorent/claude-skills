---
name: claude-model-effort
description: Use when user types /claude-model-effort, before starting a subagent or workflow agent on a Claude model (Claude Code, OpenCode with Claude) whose model or effort level must be picked, when a task seems to need a stronger or cheaper model, or when a run is about to use max effort.
---

# Picking a Claude model and an effort level

This skill and other-model-effort only ones in repository naming models and effort levels. Every other skill
leaves them out: choice made here, once, per agent started. Tables also serve other-model-effort, which maps
them onto non-Claude models.

Each task type has minimum (cheapest setting doing the job) and ceiling. Anything between is valid; start at
minimum, climb only per rule 6. Goal: best result for fewest tokens.

## Rules

Hold for every agent, any task.

1. Never `max` effort unless user names it (rule 4). Table ceiling is upper bound; nothing above it.
2. Effort sets reasoning depth, not model quality. Five levels: `low`, `medium`, `high`, `xhigh`, `max`.
   `xhigh` only for long agentic runs and decisions costly when wrong.
3. Set model and effort on agent call itself (Claude Code: `model` and `effort` parameters of Agent tool,
   or `model` and `effort` keys of agent file front matter).
4. Model or effort user or project names for this task wins, `max` included; general default for every
   subagent, such as one in CLAUDE.md, gives way to these tables.
5. Several task types in one agent: highest minimum and highest ceiling among them.
6. Task failing twice at one setting moves up one step. Raise effort one level at a time up to ceiling's
   effort, then next model at minimum's effort; ceiling's model and effort both hard limits. Past ceiling,
   split task, no bigger model.
7. No row matches: take closest row, name it next to setting.

Models, lightest first: Haiku 5.5 (fast, cheap), Sonnet 5.5 (all-round), Opus 5.5 (deep reasoning).
Fable, stronger than Opus and pricier, only when user or project names it.

## Research and reading

Mostly reading, little reasoning.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Web research: docs, watch, comparing sources | Haiku low | Sonnet low | Haiku summarises a page; crossing sources needs Sonnet low, no higher. |
| File or folder search: glob, grep, locate | Haiku low | Haiku medium | Mechanical; medium prevents early stop or skipped check. |
| File reader: a doc, a PDF, summing up existing code | Haiku low | Haiku high | One fact low; long document high, still no Sonnet. |
| Image reader: OCR, a screenshot, a chart | Haiku low | Haiku high | Readable text low; describing layout high, still no Sonnet. |
| Logs or a stack trace | Haiku medium | Sonnet medium | Much reading, little reasoning; Sonnet once cause must be traced. |

## Code and development

Core of the work.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Everyday code: a function, a component, a simple fix | Sonnet low | Sonnet medium | Low for well-framed work. |
| Script writer: short bash or Python, throwaway automation | Haiku medium | Sonnet medium | Haiku low forgets edge cases. |
| Running tests, reading the failure, fixing | Sonnet medium | Opus medium | Failing test means tracing a cause; Opus avoids fix loops. |
| Browser test: browser-bidi, screenshots, responsive | Sonnet medium | Opus medium | Gap between expected and shown is visual reasoning. |
| Git and commits: message, diff summary, simple conflict | Haiku low | Haiku medium | No deep reasoning; best place to save tokens. |
| Run upkeep: commit and push through scripts, stop your own processes, close the browser | Haiku low | Haiku medium | Every command known; scripts refuse what is wrong. |
| Technical writing: README, API explanations | Haiku medium | Sonnet medium | Sonnet keeps tone and consistency over long document. |
| Code review: a PR, traps and gaps | Sonnet medium | Opus medium | Spotting what is missing harder than fixing. |
| Multi-file refactor: rename, move, spread an API | Sonnet medium | Opus medium | Much context to keep consistent. |
| Regular expressions | Sonnet medium | Opus medium | Short but tricky; wrong regex passes simple tests. |
| SQL: joins, aggregates, a slow query | Sonnet medium | Opus medium | Bad join costs hours of database time. |
| Docker and CI/CD: Dockerfile, pipeline, deploy script | Sonnet medium | Opus medium | Errors show only at deploy, often in production. |
| External API integration: auth and errors | Sonnet medium | Opus medium | Error cases are the real work. |
| Rust systems code: borrows, lifetimes, concurrency | Sonnet medium | Opus high | Compiler guides simple errors; rest shows only in use. |
| Database migrations: Prisma, SQL, schema changes | Sonnet medium | Opus high | Passes locally, breaks in production; rollback costs more than tokens. |
| Teams app and Microsoft SDK: host, permissions | Sonnet medium | Opus medium | Little code, many unforgiving host and permission rules. |

## Code optimisation

Opus is floor: Sonnet holds too little context to see what a rewrite breaks elsewhere.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Rewriting for readability, structure or speed | Opus medium | Opus high | Medium for isolated file, high once area is shared. |
| Technical debt: dead code, duplication, useless dependencies | Opus medium | Opus high | Removing what looks unused breaks quiet features. |

## Specialised and visual

Visual and spatial work needs high floor.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| 3D model: scene, materials, geometry, export | Opus high | Opus xhigh | Below that, spatial consistency goes. |
| Shaders and GPU rendering: WGSL, wgpu, textures | Opus high | Opus xhigh | Wrong shader does not crash, shows something almost right. |
| Design and UI: mock-up, hierarchy, palette | Sonnet medium | Opus medium | Several constraints held at once. |
| Accessibility: contrast, keyboard, screen readers | Sonnet medium | Opus medium | Gaps invisible to the eye. |

## Large code and long jobs

Past a few files, a mistake costs far more than tokens: aim is not redoing work three times.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Large feature: several files, API and UI together | Opus low | Opus medium | Plan matters more than typing speed. |
| Rewrite or migration: new framework, major version | Opus medium | Opus xhigh | Whole project map must be held. |
| Understanding an unknown codebase | Sonnet medium | Opus medium | Much context to assemble. |
| Mass test generation: a whole module | Sonnet medium | Opus medium | Finding edge cases takes reasoning. |
| Long agentic task: hours, many steps, few human checks | Opus medium | Opus xhigh | Stopping early costs full relaunch. |
| Performance and profiling | Opus medium | Opus xhigh | Fix for one case can break three others; measure first. |
| Architecture and stack choices | Opus medium | Opus xhigh | Bad decision here costs days. |
| Hard debugging: reproducible but not understood, regression | Opus medium | Opus xhigh | Cheaper than three failed attempts lower. |
| Security review: injection, hardcoded secrets, vulnerable dependencies | Opus medium | Opus xhigh | Audit missing a flaw is worthless. |

## Data and content

Volume makes every token count.

| Task | Minimum | Ceiling | Why |
|---|---|---|---|
| Bulk processing: classify, extract, route hundreds of items | Haiku low | Haiku medium | Best value for volume. |
| Structured extraction: clean JSON from free text | Haiku low | Haiku medium | Form, not substance; medium avoids missing or invented fields. |
| Translation and i18n: language files, consistent tone | Haiku medium | Sonnet medium | Sonnet keeps terminology of whole file. |
| Excel and PDF generation: tables, formulas, layout | Sonnet medium | Opus medium | Real data is dirty, layout checked by eye. |

## /claude-model-effort <task>

Find matching row (several rows: rule 5, none: rule 7), answer in user's language with minimum, ceiling and
reason, two or three lines. Never answer `max`.
