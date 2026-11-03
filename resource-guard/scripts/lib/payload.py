SHELLS = {"bash", "sh", "zsh", "cmd", "pwsh", "powershell"}
COMMAND_KEYS = ("command", "cmd")
SHELL_WRAPPED = 3
SWITCHES = ("-", "/")
EXECUTABLE = ".exe"


def _program(word):
    name = word.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name[:-len(EXECUTABLE)] if name.endswith(EXECUTABLE) else name


def _joined(parts):
    if len(parts) >= SHELL_WRAPPED and _program(parts[0]) in SHELLS and parts[1].startswith(SWITCHES):
        return " ".join(parts[2:])
    return " ".join(parts)


def _text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list) and value and all(isinstance(part, str) for part in value):
        return _joined(value)
    return ""


def command_of(event):
    if not isinstance(event, dict):
        return ""
    tool_input = event.get("tool_input")
    if isinstance(tool_input, dict):
        for key in COMMAND_KEYS:
            text = _text(tool_input.get(key))
            if text:
                return text
    return _text(event.get("command"))
