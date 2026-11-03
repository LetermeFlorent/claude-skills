import re

FLAGS = re.IGNORECASE | re.MULTILINE
AI_EMAILS = (r"noreply@anthropic\.com|noreply@openai\.com|cursoragent@cursor\.com|copilot@users\.noreply\.github\.com"
             r"|copilot-swe-agent|devin-ai-integration|google-labs-jules|gemini-code-assist|claude\[bot\]")
AI_MODELS = r"claude[ -](code|opus|sonnet|haiku|fable|\d)|chatgpt|gpt-?\d|codex|copilot|cursor( agent)?\b|gemini"
TRAILER = re.compile(
    rf"^\s*(co-authored-by|co-developed-by|assisted-by|generated-by)\s*:.*({AI_EMAILS}|{AI_MODELS}|anthropic|openai)"
    r"|^\s*claude-[\w-]+\s*:|^\s*made[- ]with\s*:?\s*cursor|^\s*agent-logs-url\s*:"
    r"|generated (with|by) \[?(claude|codex|copilot|cursor|gemini|chatgpt|devin|jules|aider)"
    r"|claude\.ai/code|claude\.com/claude-code|chatgpt\.com/codex"
    rf"|{AI_EMAILS}", FLAGS)
BOT_IDENTITY = re.compile(rf"{AI_EMAILS}|\(aider\)|\bcursor agent\b|\b(copilot|claude|codex|openai|anthropic|jules"
                          r"|devin|gemini|amazon-q|kiro)[\w-]*\[bot\]", re.IGNORECASE)
AI_BRANCH = re.compile(r"(^|/)(claude|codex|copilot|cursor|devin|jules|gemini|aider|windsurf|kiro|amazonq|openhands"
                       r"|cline|junie)[/-]", re.IGNORECASE)
AI_FILES = re.compile(r"(^|/)(\.claude/|CLAUDE(\.local)?\.md$|AGENTS?\.md$|GEMINI\.md$|\.cursorrules$|\.cursor/"
                      r"|\.windsurfrules$|\.windsurf/|\.devin/|\.github/copilot-instructions\.md$"
                      r"|\.github/instructions/|\.github/agents/|\.github/prompts/|\.aider[^/]*$|\.junie/"
                      r"|\.clinerules|\.roo/|\.kiro/|\.amazonq/|\.codex/|\.gemini/|\.continue/|\.ia/)")
AI_ACTIONS = re.compile(r"claude-code-action|claude-code-base-action|codex-action|run-gemini-cli|gemini-cli"
                        r"|copilot-swe-agent|devin|aider", re.IGNORECASE)
LEFTOVER_FILES = re.compile(r"^(IMPLEMENTATION|CHANGES?|FIX(ES)?|REFACTOR(ING)?|MIGRATION|SESSION|TASK|WORK|AUDIT)"
                            r"_(SUMMARY|NOTES|PLAN|REPORT|LOG)\.md$|^(repro|scratch|debug)_\w*\.(py|js|ts|sh)$",
                            re.IGNORECASE)
GENERATORS = re.compile(r"python-docx|openpyxl|python-pptx|xlsxwriter|reportlab|pdf-lib|pypdf|fpdf|wkhtmltopdf"
                        r"|weasyprint|skia/pdf|headlesschrome|puppeteer|playwright|pdfkit|docx\.js|exceljs|sheetjs",
                        re.IGNORECASE)
PROVENANCE = (("C2PA content credentials", b"c2pa"),
              ("IPTC source type: made by a trained algorithm", b"trainedAlgorithmicMedia"),
              ("Stable Diffusion parameters chunk", b"parameters\x00"),
              ("ComfyUI workflow chunk", b"workflow\x00{"),
              ("Midjourney mark (unverified field)", b"Midjourney"))
