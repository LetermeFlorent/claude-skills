import json
import sys

FILE_TOOLS = {"Write": "written", "Edit": "edited", "MultiEdit": "edited", "NotebookEdit": "edited"}
NO_PROMPT = "PROMPT NOT FOUND"


def read_entries(path):
    entries = []
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    entries.append(json.loads(line))
                except ValueError:
                    continue
    except OSError as error:
        print(f"warning: cannot read {path}: {error}", file=sys.stderr)
    return [entry for entry in entries if isinstance(entry, dict)]


def read_meta(path):
    meta_path = path[:-len(".jsonl")] + ".meta.json" if path.endswith(".jsonl") else ""
    try:
        with open(meta_path, encoding="utf-8") as handle:
            meta = json.load(handle)
            return meta if isinstance(meta, dict) else {}
    except (OSError, ValueError):
        return {}


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
        return "\n".join(parts)
    return ""


def describe(name, args):
    if name == "Bash":
        flag = "[background] " if args.get("run_in_background") else ""
        return f"Bash {flag}{args.get('command', '')}"
    target = args.get("file_path") or args.get("description") or args.get("pattern") or ""
    return f"{name} {target}".strip()


def new_data():
    return {"prompt": "", "cwd": "", "branch": "", "first": "", "last": "", "files": {},
            "commands": [], "texts": [], "spawned": [], "followups": [], "calls": 0, "open": {}}


def add_tool_use(data, part, stamp):
    data["calls"] += 1
    name, args = part.get("name", ""), part.get("input") or {}
    if not isinstance(args, dict):
        args = {}
    data["open"][part.get("id", f"call-{data['calls']}")] = f"{stamp} {describe(name, args)}"
    if name in FILE_TOOLS and args.get("file_path"):
        data["files"].setdefault(args["file_path"], set()).add(FILE_TOOLS[name])
    elif name == "Bash":
        data["commands"].append(f"{stamp} {describe(name, args)[5:]}")
    elif name in ("Agent", "Task"):
        data["spawned"].append(f"{stamp} {args.get('description', '')} ({args.get('model', 'default')})")


def collect(entries):
    data = new_data()
    for entry in entries:
        stamp = entry.get("timestamp") or ""
        data["first"] = data["first"] or stamp
        data["last"] = stamp or data["last"]
        attachment = entry.get("attachment") if isinstance(entry.get("attachment"), dict) else {}
        if attachment.get("type") == "queued_command" and attachment.get("prompt"):
            data["followups"].append(f"{stamp} {text_of(attachment['prompt'])}")
        message = entry.get("message") if isinstance(entry.get("message"), dict) else {}
        content = message.get("content")
        if entry.get("type") == "user":
            text = text_of(content).strip()
            if not data["prompt"] and text:
                data.update(prompt=text, cwd=entry.get("cwd", ""), branch=entry.get("gitBranch", ""))
            elif isinstance(content, str) and text:
                data["followups"].append(f"{stamp} {text}")
            for part in content if isinstance(content, list) else []:
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    data["open"].pop(part.get("tool_use_id"), None)
        if entry.get("type") != "assistant" or not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text" and part.get("text", "").strip():
                data["texts"].append(part["text"].strip())
            elif isinstance(part, dict) and part.get("type") == "tool_use":
                add_tool_use(data, part, stamp)
    data["prompt"] = data["prompt"] or NO_PROMPT
    return data
