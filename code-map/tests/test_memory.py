import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

from extract import extract
from graph import Graph
from knowledge import notes, recall
from queries import unused

README = "# Tools\n\nCall `compute()` first.\n\n## Why build_all\n\nThe build_all step runs, then report.\n"


def code(defs, tokens=()):
    return {"lang": "python", "lines": 1, "defs": defs, "imports": [], "tokens": list(tokens)}


class NoteStoreTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        (self.root / "tools.py").write_text("def compute():\n    pass\n", encoding="utf-8")

    def tearDown(self):
        self.folder.cleanup()

    def test_save_list_drop(self):
        data = notes.load(self.root)
        first = notes.add(data, "compute must run before report", {"tools.py": notes.file_hash(self.root, "tools.py")})
        second = notes.add(data, "tried threads, too slow", {})
        notes.save(self.root, data)
        again = notes.load(self.root)
        self.assertEqual([n["id"] for n in again["notes"]], [first, second])
        self.assertTrue(notes.drop(again, first))
        self.assertFalse(notes.drop(again, first))
        self.assertEqual([n["text"] for n in again["notes"]], ["tried threads, too slow"])

    def test_ids_never_reused(self):
        data = notes.load(self.root)
        first = notes.add(data, "a", {})
        notes.drop(data, first)
        self.assertGreater(notes.add(data, "b", {}), first)

    def test_stale_after_file_change(self):
        data = notes.load(self.root)
        notes.add(data, "fact", {"tools.py": notes.file_hash(self.root, "tools.py")})
        note = data["notes"][0]
        self.assertFalse(notes.is_stale(self.root, note))
        (self.root / "tools.py").write_text("def compute():\n    return 1\n", encoding="utf-8")
        self.assertTrue(notes.is_stale(self.root, note))
        self.assertIn("stale", notes.line(note, True))

    def test_stale_when_file_gone(self):
        data = notes.load(self.root)
        notes.add(data, "fact", {"gone.py": "abc"})
        self.assertTrue(notes.is_stale(self.root, data["notes"][0]))


class MarkdownTest(unittest.TestCase):
    def test_headings_and_mentions(self):
        found = extract("docs/README.md", README)
        self.assertEqual(found["lang"], "markdown")
        self.assertIn(["Tools", "heading", 1], found["defs"])
        self.assertIn(["Why build_all", "heading", 5], found["defs"])
        self.assertIn("compute", found["tokens"])
        self.assertIn("build_all", found["tokens"])
        self.assertNotIn("report", found["tokens"])

    def test_doc_edges_in_graph(self):
        graph = Graph({"tools.py": code([["compute", "function", 1]]),
                       "README.md": extract("README.md", README)})
        self.assertEqual(recall.docs_about(graph, "compute"), ["README.md"])
        self.assertIn("README.md", graph.refs["compute"])

    def test_doc_mention_does_not_hide_dead_code(self):
        graph = Graph({"tools.py": code([["compute", "function", 1]]),
                       "README.md": extract("README.md", README)})
        self.assertEqual(unused(graph)[0], "tools.py:1 function compute")


class RecallTest(unittest.TestCase):
    def setUp(self):
        self.graph = Graph({"lib/tools.py": code([["compute", "function", 1]])})
        self.data = {"version": 1, "next": 3, "notes": [
            {"id": 1, "text": "compute is cached on purpose", "about": ["compute"], "hashes": {}},
            {"id": 2, "text": "deploy needs the VPN", "about": ["lib/tools.py"], "hashes": {}}]}

    def test_find_over_notes(self):
        found = recall.find_notes(self.data["notes"], ["vpn"])
        self.assertEqual([n["id"] for n in found], [2])
        self.assertEqual(recall.find_notes(self.data["notes"], ["zzzz"]), [])

    def test_notes_for_symbol_and_file(self):
        self.assertEqual([n["id"] for n in recall.notes_for(self.graph, self.data["notes"], "compute")], [1])
        self.assertEqual([n["id"] for n in recall.notes_for(self.graph, self.data["notes"], "tools.py")], [2])

    def test_about_targets(self):
        self.assertEqual(recall.files_of(self.graph, "compute"), ["lib/tools.py"])
        self.assertEqual(recall.files_of(self.graph, "tools.py"), ["lib/tools.py"])
        self.assertEqual(recall.files_of(self.graph, "nothing"), [])


if __name__ == "__main__":
    unittest.main()
