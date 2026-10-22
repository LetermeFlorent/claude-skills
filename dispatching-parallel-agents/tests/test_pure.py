import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

from plan import clean_path, load_plan
from rules import check_plan, nested


BACK = chr(92)


def plan(*agents):
    return load_plan(json.dumps({"agents": list(agents)}))


class PathTest(unittest.TestCase):
    def test_backslashes_and_case_are_normalized(self):
        self.assertEqual(clean_path(BACK.join(["C:", "Repo", "Src", ""])), "c:/repo/src")

    def test_a_folder_contains_its_files(self):
        self.assertTrue(nested("src", "src/a.py"))
        self.assertFalse(nested("src", "srcs/a.py"))


class IndependenceTest(unittest.TestCase):
    def test_distinct_files_pass(self):
        self.assertEqual(check_plan(plan({"name": "a", "writes": ["t/a.py"]}, {"name": "b", "writes": ["t/b.py"]})), [])

    def test_same_file_is_refused(self):
        found = check_plan(plan({"name": "a", "writes": ["t/a.py"]}, {"name": "b", "writes": [f"T{BACK}a.py"]}))
        self.assertEqual(len(found), 1)

    def test_folder_against_file_is_refused(self):
        found = check_plan(plan({"name": "a", "writes": ["src"]}, {"name": "b", "writes": ["src/b.py"]}))
        self.assertEqual(len(found), 1)

    def test_shared_port_and_instance(self):
        first = {"name": "a", "ports": [3000], "instances": ["Blender:1"]}
        second = {"name": "b", "ports": ["3000"], "instances": ["blender:1"]}
        self.assertEqual(len(check_plan(plan(first, second))), 2)

    def test_two_committers_in_one_tree(self):
        found = check_plan(plan({"name": "a", "commits": True}, {"name": "b", "commits": True}))
        self.assertEqual(len(found), 1)

    def test_rebuild_is_refused(self):
        self.assertEqual(len(check_plan(plan({"name": "a", "rebuild": True}))), 1)

    def test_three_heavy_agents_are_too_many(self):
        agents = [{"name": name, "heavy": True} for name in "abc"]
        self.assertEqual(len(check_plan(plan(*agents))), 1)

    def test_bad_plans_raise(self):
        with self.assertRaises(ValueError):
            load_plan("[]")


if __name__ == "__main__":
    unittest.main()
