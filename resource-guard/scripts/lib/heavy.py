import re

from common import TOOL

PROGRAMS = (
    "docker-compose", "docker", "podman", "vite", "next", "node", "npx", "pnpx", "bunx", r"python[\d.]*", "py",
    "pytest", "java", "gradlew", "gradle", "mvnw", "mvn", "cargo", "dotnet", "tauri", "tsc", "webpack", "vitest",
    "jest", "playwright", "make", "cmake", "ninja", "msbuild",
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


def is_heavy(command):
    if not command or TOOL in command.lower():
        return False
    return PATTERN.search(command) is not None
