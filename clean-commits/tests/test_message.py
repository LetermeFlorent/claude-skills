import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SIGNATURES = Path(__file__).resolve().parents[2] / "strip-ai-traces" / "scripts" / "lib" / "signatures.py"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

from message import ATTRIBUTION, check
from paths import OK_KIND, SECRET_KIND, TOOLING_KIND, classify
from scrub import _clean

FREE = {"commits": 3, "language": None, "conventional": False, "types": {}, "scopes": {}, "examples": []}
ANTHROPIC = "noreply@" + "anthropic.com"
TRAILER_LINE = f"Co-Authored-By: Claude <{ANTHROPIC}>"


class MessageTest(unittest.TestCase):
    def test_tool_trailers_are_attribution(self):
        for line in (TRAILER_LINE, "Claude-Session: https://claude" + ".ai/code/x", "Made-with: Cursor",
                     "Generated with " + "[Claude Code](https://claude" + ".com/claude-code)"):
            self.assertTrue(ATTRIBUTION.search(line), line)

    def test_a_subject_named_after_a_skill_is_not_attribution(self):
        for text in ("claude-model-effort: pick a cheaper model", "claude-skills: release v1.7",
                     "fix\n\nCo-Authored-By: Claude Dupont <claude.dupont@example.com>"):
            self.assertIsNone(ATTRIBUTION.search(text), text)
            self.assertEqual(check(text, FREE, None), [], text)

    def test_emoji_and_attribution_are_refused(self):
        self.assertIn("emoji in the message", check("fix the cart \U0001F680", FREE, None))
        self.assertIn("AI tool attribution: remove the line", check("fix\n\nClaude-Session: x", FREE, None))

    def test_scrub_keeps_the_subject_and_drops_the_trailer(self):
        text = f"claude-model-effort: pick\n\nbody\n\n{TRAILER_LINE}\n"
        self.assertEqual(_clean(text), "claude-model-effort: pick\n\nbody\n")

    @unittest.skipUnless(SIGNATURES.exists(), "strip-ai-traces is not installed next to this skill")
    def test_same_pattern_as_strip_ai_traces(self):
        spec = importlib.util.spec_from_file_location("signatures", SIGNATURES)
        signatures = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(signatures)
        self.assertEqual(ATTRIBUTION.pattern, signatures.TRAILER.pattern)
        self.assertEqual(ATTRIBUTION.flags, signatures.TRAILER.flags)


class PathsTest(unittest.TestCase):
    def kind(self, name, text=""):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")
        return classify(root, {"path": name, "new": True, "deleted": False})[0]

    def test_kinds(self):
        self.assertEqual(self.kind(".env"), SECRET_KIND)
        self.assertEqual(self.kind(".env.example"), OK_KIND)
        self.assertEqual(self.kind("config.ts", "key = 'sk-ant-" + "a" * 30 + "'"), SECRET_KIND)
        self.assertEqual(self.kind(".ia/plan.md"), TOOLING_KIND)
        self.assertEqual(self.kind("src/app.ts", "export {}"), OK_KIND)


if __name__ == "__main__":
    unittest.main()
