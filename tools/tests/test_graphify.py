import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import graphify

SKILL = '---\nname: graphify\ndescription: "Use for any question about a codebase."\n---\n\n# /graphify\n'


class GraphifyTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="graphify test "))
        self.addCleanup(shutil.rmtree, self.root)
        self.config = self.root / "config"
        self.state = self.root / "state" / "graphify.json"
        self.staged = self.root / "staged"
        self.staged.mkdir()
        (self.staged / "SKILL.md").write_text(SKILL, encoding="utf-8")

    def index(self, version):
        path = self.root / "index.json"
        path.write_text(json.dumps({"info": {"version": version}}), encoding="utf-8")
        return mock.patch.dict(os.environ, {graphify.INDEX_VAR: path.as_uri()})

    def test_description_is_narrowed_to_large_projects(self):
        text = graphify.narrow(SKILL)
        self.assertIn("Use only in a large codebase", text)
        self.assertNotIn("any question", text)
        self.assertTrue(text.endswith("# /graphify\n"))

    def test_placed_skill_is_marked_ours(self):
        dest = graphify.skill_dir(self.config)
        graphify.place_skill(self.staged, dest)
        self.assertTrue(graphify.is_ours(dest))
        self.assertIn("large codebase", (dest / "SKILL.md").read_text(encoding="utf-8"))

    def test_empty_staging_keeps_the_installed_skill(self):
        dest = graphify.skill_dir(self.config)
        graphify.place_skill(self.staged, dest)
        with self.assertRaises(FileNotFoundError):
            graphify.place_skill(self.root / "missing", dest)
        self.assertTrue((dest / "SKILL.md").is_file())

    def test_foreign_skill_is_left_alone(self):
        dest = graphify.skill_dir(self.config)
        dest.mkdir(parents=True)
        ok, text = graphify.install_now(self.config, self.state, "1.0.0")
        self.assertFalse(ok)
        self.assertIn("not ours", text)

    def test_new_version_is_wanted_then_up_to_date(self):
        with self.index("2.0.0"):
            self.assertEqual(graphify.needed(self.config, self.state)[0], "2.0.0")
            graphify.place_skill(self.staged, graphify.skill_dir(self.config))
            graphify.write_json(self.state, {"version": "2.0.0"})
            self.assertEqual(graphify.needed(self.config, self.state), (None, "graphify: up to date (2.0.0)"))

    def test_offline_keeps_what_is_there(self):
        with mock.patch.dict(os.environ, {graphify.INDEX_VAR: (self.root / "none.json").as_uri()}):
            latest, text = graphify.needed(self.config, self.state)
        self.assertIsNone(latest)
        self.assertIn("could not reach PyPI", text)


if __name__ == "__main__":
    unittest.main()
