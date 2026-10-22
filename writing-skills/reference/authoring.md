# Authoring guide, condensed

What still applies from Anthropic's "Skill authoring best practices" (platform.claude.com, Agent
Skills), adjusted to this repository. Where the two disagree, this repository's rule is given with its reason.

## Concise

The agent reading a skill is already capable; each paragraph has to earn its tokens. Does the agent
need this? Does it know it already? At start-up only the name and the description of every skill
load. `SKILL.md` loads when the skill triggers, any other file only when read. Once loaded, every
line competes with the conversation for room.

A pdfplumber example in five lines beats three paragraphs on what a PDF is and why a library helps.

## Freedom matched to fragility

Steps in prose when several approaches are valid and the context decides, as in a code review. A
template or a script with parameters when a preferred pattern exists and some variation is fine. One
exact command, with "do not change the flags", when the operation is fragile or must run in one
order, as in a migration. A narrow bridge gets guardrails; an open field gets a direction.

## Name and description

The official guide wants the description to say what the skill does and when to use it. Here
it says when, and only when. The superpowers authors saw an agent follow a workflow summary in a
description ("code review between tasks") and run one review where the body asked for two; once the
description held triggers only, the agent read the body and ran both.

The rest of the advice holds. Third person, since the description is injected into the system
prompt. Specific key terms: the words an agent would search for, such as error messages, symptoms,
synonyms, tool names and file types. A name of 64 characters at most and a description of 1024 at
most. Names verb-first or gerunds (`processing-pdfs`, `writing-plans`), never vague (`helper`,
`utils`, `tools`), consistent across the collection.

## Progressive disclosure

`SKILL.md` works as a table of contents that sends the agent to the file it needs.

- One level deep. Every reference file is named from `SKILL.md`. A file named only from another
  reference tends to be read in part, with `head`, or not at all.
- Past 100 lines, a contents list at the top, so a partial read still shows the whole scope.
- Split by domain (`reference/finance.md`, `reference/sales.md`) so a task loads its part only.
- Anthropic puts the limit of the body at 500 lines; this repository aims for about 250.

## Workflows and feedback loops

A complex task gets numbered steps. A long one gets a checklist the agent copies into its answer and
ticks as it goes.

Quality comes from the validation loop: run the validator, fix, run it again, go on only once it
passes. The validator can be a script or a style guide read line by line. For a batch or a
destructive change, plan, validate, then execute: the agent writes its plan as a file
(`changes.json`), a script checks it with precise errors ("field `signature_date` not found;
available: `customer_name`, `order_total`"), and only then does anything change.

## Content

The body holds what the agent cannot guess, worded so it stays true.

- Nothing that turns false at a date. An old way that must stay gets one line saying it is old.
- One term per concept, kept throughout: always "field", never "box" in one place and "element" in
  the next.
- A strict template ("use exactly this structure") when something downstream checks the format; a
  flexible one ("a sensible default, adapt it") otherwise.
- Input and output pairs when style is the point, as with commit messages.
- A decision point as a condition: creating a document goes one way, editing one goes another.
- A default plus one escape, never five equal options: pdfplumber, and for scanned pages pdf2image
  with OCR.

## Scripts

A script that handles the missing file or the refused permission is worth more than one that fails
and leaves the agent to guess. Here that means the guard of `format.md`: the tool, the error,
the command by hand, exit 2 for a refusal and 1 for a failure.

The guide asks for constants explained by a comment. Code here carries no comments, so the name says
why (`REQUEST_TIMEOUT_SECONDS`), and the value is computed or read from config when it can be.

Say whether the agent runs a script or reads it as the reference of an algorithm. Running is the
default: the output costs tokens, the source does not.

Forward slashes in every path, Windows included. Never assume a package is installed: standard
library first, any dependency named in `SKILL.md`. MCP tools by the full name the session lists
(`mcp__github__create_issue`), so the agent finds the right server among several. When an input can
be rendered, let the agent look at it, shrunk first: a full HD screenshot costs about 2,760 tokens,
one 1024 pixels wide about 790.

## Models

A skill adds to a model, and what is enough for opus can be too thin for haiku. Here subjects
run on sonnet; add a run on the model that will actually load the skill when it is another one.

## Watching an agent use the folder

Read how subjects move through the skill, beyond whether they succeed. A file read in an unexpected
order means the structure is less obvious than it looked. A reference never opened is badly signalled
or useless. A file read on every run belongs in `SKILL.md`. A link not followed needs to be named
more plainly, with when to read it.
