# Documents, notebooks, images and traces

A delivered file carries its production history in fields nobody reads until someone does. Check them
before a file leaves the machine; `scan.py` reads them for you.

## Office documents

DOCX, XLSX, PPTX and ODF files keep their metadata in `docProps/app.xml`, `docProps/core.xml` or
`meta.xml`. The fields that give a generator away: `Application`, `AppVersion`, `creator`,
`lastModifiedBy`, `generator`, `Company`, `TotalTime`, `revision`, `editing-cycles`.

Measured on 2026-10-22 with openpyxl 3.1.5: `Application` is `Microsoft Excel Compatible / Openpyxl
3.1.5` and `creator` is `openpyxl`. python-docx writes `python-docx` as author and python-pptx
`python-pptx` (reported, not measured here). A long document with no editing time and a single revision
is inconsistent whatever its content: the scan says so.

Set the author fields at generation to the user's name when the user gives it (`core_properties.author`
in python-docx and python-pptx, `properties.creator` and `properties.lastModifiedBy` in openpyxl). Never
write a fake application name. For the rest, tell the user once that the file names its library, and
that opening and saving it again in the target application rewrites the fields.

## PDF

`/Producer` and `/Creator` in the document information dictionary, `pdf:Producer` and
`xmp:CreatorTool` in the XMP packet. Measured: pypdf writes `/Producer (pypdf)`. Reported: ReportLab
writes `ReportLab PDF Library - www.reportlab.com`; browsers write `Skia/PDF` with `HeadlessChrome`;
wkhtmltopdf, WeasyPrint, Puppeteer and Playwright name themselves. Also check `CreationDate` against
`ModDate`, and the `Author` field. pypdf can set the fields with `writer.add_metadata`; the same rule
applies: the user's name as author, no invented producer.

## Notebooks

`execution_count` all empty, or running 1, 2, 3 with no gap, is what a fresh generated run looks like.
Run the notebook for real, or clear the outputs on purpose. Markdown cells of the same length in a row
read as generated.

## Images

Never strip the provenance of a generated image. These marks tell the viewer the image was made by a
model, and platforms and laws rely on them: a C2PA manifest (content credentials), the IPTC digital
source type `trainedAlgorithmicMedia`, the Stable Diffusion `parameters` text chunk, the ComfyUI
`prompt` and `workflow` chunks, a Midjourney field, and SynthID inside the pixels of Google images,
which no metadata tool removes. The scan reports them; you say they are there, once.

A photograph or a drawing made by the user has no such mark; when one shows up, the image came from a
generator and the user should know before publishing it.

## Paths and sandbox signatures

A file mentioning `/mnt/data/` (ChatGPT code interpreter), `/mnt/user-data/` or `/home/claude/`
(claude.ai), a `%TEMP%` path, or a generic name such as `output.docx` or `final_v2.pdf`, shows where it
was produced. Use the project's names and paths.

## Artifacts and exports

Never publish a claude.ai artifact or a Cowork export without reading its metadata header: `mcpTools`
and `mcpServerNames` list the connectors that were plugged in. Deliver a local file and give
its path instead of an artifact.

## Session traces

Never share a transcript from `~/.claude/projects/<project>/<session>.jsonl`, nor a Codex or Cursor
session log: they hold every prompt, every file read and every tool output in clear, `.env` contents
included, and live API keys have been found in them. Never read a secrets file without need: its value
would be stored there for good.

Never share a capture of the terminal: the box drawing, the context bars and the grey italic rendering
of the reasoning identify the tool whatever the content says.
