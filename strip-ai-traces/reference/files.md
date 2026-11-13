# Documents, notebooks, images and traces

Check delivered files before they leave the machine; `scan.py` reads these fields.

## Office documents

DOCX, XLSX, PPTX and ODF keep metadata in `docProps/app.xml`, `docProps/core.xml` or `meta.xml`. Giveaway fields: `Application`, `AppVersion`, `creator`, `lastModifiedBy`, `generator`, `Company`, `TotalTime`, `revision`, `editing-cycles`. openpyxl writes `Application` as `Microsoft Excel Compatible / Openpyxl 3.1.5` and `creator` as `openpyxl`; python-docx and python-pptx write their own name as author. Long document with no editing time and one revision gets flagged.

Set author fields at generation to the user's name when given (`core_properties.author` in python-docx and python-pptx, `properties.creator` and `lastModifiedBy` in openpyxl). Never invent an application name. Otherwise tell user once that the file names its library and re-saving it in the target application rewrites the fields.

## PDF

`/Producer` and `/Creator` in the info dictionary, `pdf:Producer` and `xmp:CreatorTool` in XMP. pypdf writes `/Producer (pypdf)`; ReportLab, Skia/PDF with HeadlessChrome, wkhtmltopdf, WeasyPrint, Puppeteer and Playwright name themselves. Compare `CreationDate` with `ModDate`, check `Author`. pypdf sets fields with `writer.add_metadata`; same rule: user's name, no invented producer.

## Notebooks

`execution_count` all empty, or running 1, 2, 3 with no gap, looks generated. Run the notebook for real or clear outputs on purpose.

## Images

Never strip provenance of a generated image: C2PA manifest, IPTC source type `trainedAlgorithmicMedia`, Stable Diffusion `parameters` chunk, ComfyUI `prompt` and `workflow` chunks, Midjourney field, SynthID in pixels (no metadata tool removes it). Say once it is there. Photo or drawing by the user has none; if one shows up, tell user the image came from a generator.

## Paths and exports

`/mnt/data/` (ChatGPT interpreter), `/mnt/user-data/`, `/home/claude/` (claude.ai), a `%TEMP%` path, or names like `output.docx` and `final_v2.pdf` show where a file was made: use the project's names. Never publish a claude.ai artifact or Cowork export without reading its metadata header (`mcpTools`, `mcpServerNames` list plugged connectors); deliver a local file, give its path.

## Session traces

Never share a transcript (`~/.claude/projects/<project>/<session>.jsonl`, Codex or Cursor logs): holds every prompt, file read and tool output in clear, `.env` contents and live API keys included. Never share a terminal capture: box drawing, context bars and grey italic reasoning identify the tool.
