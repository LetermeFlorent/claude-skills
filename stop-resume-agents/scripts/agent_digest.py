import argparse
import glob
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transcript import collect, read_entries, read_meta

NO_AGENT = "NO_AGENT"


def default_config():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def latest_session(config):
    dirs = glob.glob(os.path.join(config, "projects", "*", "*", "subagents"))
    if not dirs:
        return ""
    return os.path.basename(os.path.dirname(max(dirs, key=os.path.getmtime)))


def find_transcripts(config, session):
    found = {}
    others = sorted(glob.glob(os.path.join(os.path.expanduser("~"), ".claude*")))
    for root in [config] + others:
        pattern = os.path.join(root, "projects", "*", session, "subagents", "agent-*.jsonl")
        for path in glob.glob(pattern):
            found.setdefault(os.path.basename(path)[len("agent-"):-len(".jsonl")], path)
    temp = os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp"
    for path in glob.glob(os.path.join(temp, "claude", "*", session, "tasks", "a*.output")):
        found.setdefault(os.path.basename(path)[:-len(".output")], path)
    return found


def fence(text):
    return "````text\n" + (text.strip() or "none") + "\n````"


def render(agent_id, path, tail):
    meta, data = read_meta(path), collect(read_entries(path))
    report = next((t for t in reversed(data["texts"]) if "AGENT REPORT" in t), "")
    lines = [f"## Agent {agent_id}", "",
             f"description: {meta.get('description', 'unknown')}",
             f"type: {meta.get('agentType', 'unknown')}, model: {meta.get('model', 'default')}, "
             f"effort: {meta.get('effort', 'default')}, depth: {meta.get('spawnDepth', 1)}",
             f"finished flag: {meta.get('finished', 'unknown')}, tool calls: {data['calls']}",
             f"cwd: {data['cwd'] or 'unknown'}, git branch: {data['branch'] or 'none'}",
             f"first activity: {data['first']}, last activity: {data['last']}",
             f"transcript: {path}", "", "### Original prompt", fence(data["prompt"]), "",
             "### Pending at end (tool calls with no result: what it was inside when stopped)",
             fence("\n".join(data["open"].values())), "", "### Files touched by Write or Edit"]
    lines += [f"- {name} ({', '.join(sorted(kinds))})" for name, kinds in data["files"].items()] or ["none"]
    lines += ["", f"### Last {tail} shell commands", fence("\n".join(data["commands"][-tail:]))]
    lines += ["", "### Subagents it spawned", fence("\n".join(data["spawned"]))]
    lines += ["", "### Messages it received after the prompt", fence("\n".join(data["followups"]))]
    lines += ["", "### Its report", fence(report)]
    lines += ["", "### Its last words", fence(data["texts"][-1] if data["texts"] else "")]
    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(description="Digest the subagent transcripts of a Claude Code session.")
    parser.add_argument("--session", default=os.environ.get("CLAUDE_CODE_SESSION_ID", ""))
    parser.add_argument("--latest", action="store_true", help="no session id known: use the newest session")
    parser.add_argument("--config", default=default_config())
    parser.add_argument("--agent", action="append", default=[], help="agent id, repeatable")
    parser.add_argument("--tail", type=int, default=15)
    parser.add_argument("--list", action="store_true", help="print agent ids only")
    parser.add_argument("--out", default="", help="write the digest to this file")
    return parser.parse_args()


def write_out(path, body, count):
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(body)
    print(f"digest written to {path} ({count} agent(s))")


def main():
    args = parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    session = args.session
    if not session and not args.latest:
        print("no session id: CLAUDE_CODE_SESSION_ID is empty. Pass --session <id>, "
              "or --latest and check that the agent ids it shows are yours.")
        sys.exit(3)
    if not session:
        session = latest_session(args.config)
        print(f"warning: using the newest session {session or 'none'}, check it is this one", file=sys.stderr)
    transcripts = find_transcripts(args.config, session) if session else {}
    wanted = {k: v for k, v in transcripts.items() if not args.agent or k in args.agent}
    missing = [a for a in args.agent if a not in transcripts]
    if args.list:
        print("\n".join(sorted(wanted)) or NO_AGENT)
        return
    header = f"# Subagent digest, session {session or 'unknown'}, {len(wanted)} agent(s)\n\n"
    header += "".join(f"No transcript found for agent {a}.\n" for a in missing)
    body = header + ("\n".join(render(k, v, args.tail) for k, v in sorted(wanted.items())) or "No subagent found.\n")
    if args.out:
        write_out(args.out, body, len(wanted))
    else:
        sys.stdout.write(body)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f"agent_digest failed: {error!r}. Do not open transcripts with cat or Read: take the agent "
              "list from ListAgents and your context, and fill each section from its report and git.")
        sys.exit(2)
