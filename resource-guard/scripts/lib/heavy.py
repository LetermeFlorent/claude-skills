import re

PROGRAMS = (
    "docker-compose", "docker", "podman", "vite", "next", "node", "npx", "pnpx", "bunx", r"python[\d.]*", "py",
    "pytest", "java", "gradlew", "gradle", "mvnw", "mvn", "cargo", "dotnet", "tauri", "tsc", "webpack", "vitest",
    "jest", "playwright", "make", "cmake", "ninja", "msbuild", r"pip[\d.]*", "uv", "uvx", "deno", "rustc",
)
MANAGERS = "npm|pnpm|yarn|bun"
MANAGER_VERBS = "run-script|run|install|i|ci|add|test|t|build|exec|x|dlx|start|dev|tauri|vite|next"
GO_VERBS = "build|test|run|install|generate|vet"
SCRIPT_NAMES = "build|test"
SUFFIX = r"(?:\.exe|\.cmd|\.bat|\.sh|\.ps1|\.py)?"
START = r"(?:^|&&|\|\||[;&|(\n`]|\$\()\s*"
ENV = r"(?:\w+=\S*\s+)*"
WRAPPER = r"(?:(?:sudo|nice|time|env|nohup|exec|command|start)\s+(?:[-/]\S+\s+(?:\d+\s+)?)*(?:\w+=\S*\s+)*)*"
SHELL = r"(?:(?:bash|sh|zsh|cmd|pwsh|powershell)(?:\.exe)?\s+(?:[-/]\w+\s+)*[\"']?)?"
PATH = r"(?:[\"']?[\w.~:/\\-]*[/\\])?"
END = r"[\"']?(?=\s|$|[;&|)`])"
TARGET = (
    rf"(?:(?:{'|'.join(PROGRAMS)}){SUFFIX}{END}"
    rf"|(?:{MANAGERS}){SUFFIX}\s+(?:-\S+\s+)*(?:{MANAGER_VERBS})\b"
    rf"|yarn{SUFFIX}\s*(?=$|[;&|)`\"'])"
    rf"|go{SUFFIX}\s+(?:{GO_VERBS})\b"
    rf"|[\w.~:/\\-]*[/\\](?:{SCRIPT_NAMES}){SUFFIX}{END}"
    rf"|(?:{SCRIPT_NAMES})\.(?:sh|bat|cmd|ps1){END})"
)
PATTERN = re.compile(START + ENV + WRAPPER + SHELL + WRAPPER + PATH + TARGET, re.IGNORECASE)
LIGHT_SCRIPTS = (
    r"(?:browser-bidi[/\\]scripts|\$\{?S\}?)[/\\]bidi",
    r"clean-code[/\\]scripts[/\\](?:findings|score|plan_check|measure)",
    r"strip-ai-traces[/\\]scripts[/\\]scan",
    r"clean-commits[/\\]scripts[/\\]state",
    r"progress-board[/\\]server",
    r"stop-resume-agents[/\\]scripts[/\\](?:agent_digest|resume_file|resume_check)",
)
LIGHT_SCRIPT = re.compile(
    rf"\bpy(?:thon[\d.]*)?(?:\.exe)?[\"']?(?:\s+-\w+)*\s+[\"']?[^\s\"';&|]*?"
    rf"(?:(?:{'|'.join(LIGHT_SCRIPTS)})\.py|limited-run[/\\]scripts[/\\]run\.py(?=[\"']?\s+(?:list|stop)\b))",
    re.IGNORECASE,
)
GUARD_CALL = re.compile(r"resource-guard[/\\]scripts[/\\]guard\.py", re.IGNORECASE)
HEREDOC = re.compile(r"<<-?[ \t]*([\"']?)(\w+)\1[^\n]*\n(?:.*?\n)?[ \t]*\2(?=\s|$|\))", re.DOTALL)
QUOTED = r"\"(?:[^\"\\]|\\.)*\"|'[^']*'"
TEXT_ARGUMENT = re.compile(
    rf"((?:\s(?:-m|--message|--grep|-e|--regexp)(?:=|\s+)|\b(?:rg|grep|egrep|fgrep)(?:\.exe)?\s+(?:-\S+\s+)*))"
    rf"(?:{QUOTED})"
)


def is_heavy(command):
    if not command or GUARD_CALL.search(command):
        return False
    text = TEXT_ARGUMENT.sub(r"\1''", HEREDOC.sub(" ", command))
    return PATTERN.search(LIGHT_SCRIPT.sub(" ", text)) is not None
