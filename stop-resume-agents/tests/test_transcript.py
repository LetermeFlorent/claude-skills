import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

import agent_digest
import transcript


class Transcript(unittest.TestCase):
    ENTRIES = [
        {"type": "user", "timestamp": "t1", "cwd": "/p", "gitBranch": "main",
         "message": {"content": "Do the work"}},
        {"type": "assistant", "timestamp": "t2", "message": {"content": [
            {"type": "text", "text": "starting"},
            {"type": "tool_use", "id": "u1", "name": "Write", "input": {"file_path": "/p/a.py"}},
            {"type": "tool_use", "id": "u2", "name": "Bash", "input": {"command": "make", "run_in_background": True}},
            {"type": "tool_use", "id": "u3", "name": "Agent", "input": {"description": "child", "model": "sonnet"}}]}},
        {"type": "user", "timestamp": "t3", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "u1"}, {"type": "tool_result", "tool_use_id": "u3"}]}},
        {"type": "user", "timestamp": "t4", "message": {"content": "also do this"}},
        {"type": "assistant", "timestamp": "t5", "message": {"content": [
            {"type": "text", "text": "AGENT REPORT\nStatus: partial\nEND REPORT"}]}},
    ]

    def test_collect(self):
        data = transcript.collect(self.ENTRIES)
        self.assertEqual((data["prompt"], data["cwd"], data["branch"]), ("Do the work", "/p", "main"))
        self.assertEqual((data["first"], data["last"], data["calls"]), ("t1", "t5", 3))
        self.assertEqual(data["files"], {"/p/a.py": {"written"}})
        self.assertEqual(data["commands"], ["t2 [background] make"])
        self.assertEqual(data["spawned"], ["t2 child (sonnet)"])
        self.assertEqual(data["followups"], ["t4 also do this"])
        self.assertEqual(list(data["open"].values()), ["t2 Bash [background] make"])

    def test_empty_transcript_has_no_prompt(self):
        self.assertEqual(transcript.collect([])["prompt"], transcript.NO_PROMPT)

    def test_read_entries_skips_garbage(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, "agent-a1.jsonl")
            path.write_text(json.dumps({"type": "user"}) + "\nnot json\n[1]\n", encoding="utf-8")
            self.assertEqual(transcript.read_entries(str(path)), [{"type": "user"}])
            self.assertEqual(transcript.read_meta(str(path)), {})

    def test_digest_renders_one_agent(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder, "agent-a1.jsonl")
            path.write_text("\n".join(json.dumps(e) for e in self.ENTRIES), encoding="utf-8")
            Path(folder, "agent-a1.meta.json").write_text('{"description": "fix", "model": "sonnet"}', encoding="utf-8")
            text = agent_digest.render("a1", str(path))
        self.assertIn("## Agent a1", text)
        self.assertIn("description: fix", text)
        self.assertIn("Do the work", text)
        self.assertIn("t2 Bash [background] make", text)
        self.assertIn("Status: partial", text)

    def test_find_transcripts_reads_the_config_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            subagents = Path(folder, "projects", "proj", "sess-unit-test", "subagents")
            subagents.mkdir(parents=True)
            Path(subagents, "agent-a1.jsonl").write_text("", encoding="utf-8")
            found = agent_digest.find_transcripts(folder, "sess-unit-test")
            self.assertEqual(list(found), ["a1"])
            self.assertEqual(agent_digest.latest_session(folder), "sess-unit-test")

    def test_build_reports_missing_agents(self):
        body, wanted = agent_digest.build("s", {}, ["zz"])
        self.assertEqual(wanted, {})
        self.assertIn("No transcript found for agent zz.", body)
        self.assertIn("No subagent found.", body)


if __name__ == "__main__":
    unittest.main()
