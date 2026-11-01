# Authoring guide, condensed

What still applies from Anthropic's "Skill authoring best practices" (platform.claude.com, Agent
Skills) and is not already in `SKILL.md`, adjusted to this repository. Where the two disagree, this
repository's rule is given with its reason.

## Description

The official guide wants the description to say what the skill does and when to use it. Here it says
when, and only when: an agent that found a workflow summary in a description ("code review between
tasks") ran one review where the body asked for two, and once the description held triggers only it
read the body and ran both.

The rest of the advice holds. Third person, since the description is injected into the system prompt.
Specific key terms: the words an agent would search for, such as error messages, symptoms, synonyms,
tool names and file types.

## Progressive disclosure

A reference file named only from another reference tends to be read in part, with `head`, or not at
all: every one is named from `SKILL.md`. Split by domain (`reference/finance.md`,
`reference/sales.md`) so a task loads its part only. Anthropic puts the limit of the body at 500
lines; this repository aims for about 250.

## Feedback loops

Quality comes from the validation loop: run the validator, fix, run it again, go on only once it
passes. The validator can be a script or a style guide read line by line. For a batch or a
destructive change, plan, validate, then execute: the agent writes its plan as a file
(`changes.json`), a script checks it with precise errors ("field `signature_date` not found;
available: `customer_name`, `order_total`"), and only then does anything change.

A template is strict ("use exactly this structure") when something downstream checks the format, and
flexible ("a sensible default, adapt it") otherwise. A default plus one escape beats five equal
options: pdfplumber, and for scanned pages pdf2image with OCR.

## Scripts

A script that handles the missing file or the refused permission is worth more than one that fails
and leaves the agent to guess: the guard of `format.md`. Code here carries no comments, so the name
says why a constant has its value (`REQUEST_TIMEOUT_SECONDS`).

Say whether the agent runs a script or reads it as the reference of an algorithm. Running is the
default: the output costs tokens, the source does not. Forward slashes in every path, Windows
included. Never assume a package is installed: standard library first, any dependency named in
`SKILL.md`. MCP tools by the full name the session lists (`mcp__github__create_issue`), so the agent
finds the right server among several. When an input can be rendered, let the agent look at it, shrunk
first: a full HD screenshot costs about 2,760 tokens, one 1024 pixels wide about 790.

## Models

A skill adds to a model, and what is enough for opus can be too thin for haiku. Here subjects run on
sonnet; add a run on the model that will actually load the skill when it is another one.

## Watching an agent use the folder

Read how subjects move through the skill, beyond whether they succeed. A file read in an unexpected
order means the structure is less obvious than it looked. A reference never opened is badly signalled
or useless. A file read on every run belongs in `SKILL.md`. A link not followed needs to be named
more plainly, with when to read it.
