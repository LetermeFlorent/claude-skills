import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

import queries
from algo import components, score, shortest_path, words
from extract import extract, tokens_of
from graph import Graph, target_of
from store import unchanged

SAMPLES = {
    "a.py": ("import os\nfrom .b import thing\nLIMIT = 3\n\nclass Box:\n    def open(self):\n        pass\n\n"
             "def build():\n    return Box()\n",
             {"Box": "class", "open": "method", "build": "function", "LIMIT": "const"}, {"os", ".b", ".b.thing"}),
    "a.ts": ("import { x } from './util';\nexport interface Shape {}\nexport async function draw() {}\n"
             "export const SIZE = 4;\nclass View {\n  render(a: number) {\n  }\n}\n",
             {"Shape": "type", "draw": "function", "SIZE": "const", "View": "class", "render": "method"}, {"./util"}),
    "a.go": ('package a\nimport (\n\t"fmt"\n\tlog "github.com/x/log"\n)\ntype Server struct{}\n'
             "func (s *Server) Start() {}\nfunc Run() {}\n",
             {"Server": "type", "Start": "function", "Run": "function"}, {"fmt", "github.com/x/log"}),
    "a.rs": ("use crate::core::Engine;\nmod util;\npub struct Engine {}\npub async fn go() {}\nconst MAX: u8 = 1;\n",
             {"Engine": "type", "go": "function", "MAX": "const"}, {"crate::core::Engine", "util"}),
    "A.java": ("import java.util.List;\npublic class A {\n    public static void main(String[] a) {\n    }\n}\n",
               {"A": "class", "main": "method"}, {"java.util.List"}),
    "a.kt": ("import a.b.C\nclass K\nprivate fun helper() {}\nval LIMIT = 1\n",
             {"K": "class", "helper": "function", "LIMIT": "const"}, {"a.b.C"}),
    "a.cs": ("using System.Text;\npublic class P {\n    public static int Total(int x) { return x; }\n}\n",
             {"P": "class", "Total": "method"}, {"System.Text"}),
    "a.c": ('#include "util.h"\n#define LIMIT 3\nstruct node {};\nstatic int add(int a, int b)\n{\n}\n',
            {"LIMIT": "const", "node": "type", "add": "function"}, {"util.h"}),
    "a.php": ("<?php\nuse App\\Models\\User;\nclass Repo {\n  public function find() {}\n}\n",
              {"Repo": "class", "find": "function"}, {"App\\Models\\User"}),
    "a.rb": ("require 'json'\nrequire_relative 'helper'\nclass Foo\n  def bar?\n  end\nend\n",
             {"Foo": "class", "bar?": "function"}, {"json", "helper"}),
    "a.swift": ("import Foundation\nstruct Point {}\npublic func move() {}\n",
                {"Point": "class", "move": "function"}, {"Foundation"}),
    "a.lua": ("local Util = require(script.Parent.Util)\nlocal function step() end\nfunction M.go() end\n",
              {"step": "function", "go": "function"}, {"Util"}),
    "a.sh": ("source ./lib.sh\nbuild() {\n  echo\n}\nfunction clean {\n}\n",
             {"build": "function", "clean": "function"}, {"./lib.sh"}),
}


def entry(defs, imports=(), tokens=(), lines=1):
    return {"lang": "python", "lines": lines, "defs": defs, "imports": list(imports), "tokens": list(tokens)}


class ExtractTest(unittest.TestCase):
    def test_each_language(self):
        for path, (text, expected, imports) in SAMPLES.items():
            found = extract(path, text)
            self.assertEqual({n: k for n, k, _ in found["defs"]}, expected, path)
            self.assertEqual(set(found["imports"]), imports, path)

    def test_line_numbers(self):
        found = extract("a.py", SAMPLES["a.py"][0])
        self.assertIn(["build", "function", 9], found["defs"])

    def test_unknown_extension_is_a_file_node(self):
        found = extract("notes.txt", "def foo(): pass\n")
        self.assertEqual((found["lang"], found["defs"], found["tokens"]), ("other", [], []))

    def test_broken_python_keeps_tokens(self):
        found = extract("bad.py", "def (:\nprint(helper)\n")
        self.assertEqual(found["defs"], [])
        self.assertIn("helper", found["tokens"])

    def test_tokens_skip_own_definition_line_and_short_names(self):
        defs = [["alpha", "function", 1]]
        self.assertEqual(tokens_of("def alpha(beta):\n    gamma(ab)\n", defs), ["beta", "def", "gamma"])


class RankTest(unittest.TestCase):
    def test_words_split_case_and_separators(self):
        self.assertEqual(words("syncSkills_now"), ["sync", "skills", "now"])
        self.assertEqual(words("HTTPServer"), ["http", "server"])

    def test_score_prefers_name_over_path(self):
        self.assertGreater(score(["push"], "push", "a/b.py"), score(["push"], "other", "a/push.py"))
        self.assertEqual(score(["zzz"], "push", "a/b.py"), 0)

    def test_score_rewards_every_word(self):
        self.assertGreater(score(["push", "github"], "push_github", "x.py"), score(["push", "github"], "push", "x.py"))


class GraphAlgoTest(unittest.TestCase):
    def test_cycles(self):
        adj = {"a": ["b"], "b": ["c"], "c": ["a", "d"], "d": [], "e": ["e"]}
        self.assertEqual(components(adj), [["a", "b", "c"]])

    def test_shortest_path(self):
        adj = {"a": {"b", "c"}, "b": {"d"}, "c": {"e"}, "e": {"d"}}
        self.assertEqual(shortest_path(adj, ["a"], {"d"}), ["a", "b", "d"])
        self.assertIsNone(shortest_path(adj, ["d"], {"a"}))

    def test_cache_decision(self):
        self.assertTrue(unchanged({"sig": "1:2"}, "1:2"))
        self.assertFalse(unchanged({"sig": "1:2"}, "1:3"))
        self.assertFalse(unchanged(None, "1:2"))

    def test_import_targets(self):
        self.assertEqual(target_of("pkg/a.py", ".b"), ("pkg/b", True))
        self.assertEqual(target_of("pkg/a.py", "..b"), ("b", True))
        self.assertEqual(target_of("src/a.ts", "./util.ts"), ("src/util", True))
        self.assertEqual(target_of("a.py", "x.y.z"), ("x/y/z", False))


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.graph = Graph({
            "app/main.py": entry([["start", "function", 1]], ["lib.tools"], ["compute", "start"]),
            "lib/tools.py": entry([["compute", "function", 1], ["orphan", "function", 5]], [], ["tools"]),
            "lib/__init__.py": entry([["exported", "function", 1]]),
        })

    def test_import_resolution(self):
        self.assertEqual(self.graph.imports, {"app/main.py": ["lib/tools.py"]})

    def test_references_skip_defining_file(self):
        self.assertEqual(self.graph.refs, {"compute": ["app/main.py"]})

    def test_unused_ignores_entry_points_and_index_files(self):
        found = queries.unused(self.graph)
        self.assertIn("lib/tools.py:5 function orphan", found)
        self.assertFalse(any("exported" in line or "start" in line for line in found))

    def test_find_and_no_match(self):
        self.assertTrue(queries.find(self.graph, ["compute"], 500)[0].startswith("lib/tools.py:1 function compute"))
        self.assertTrue(queries.find(self.graph, ["zzzz"], 500)[0].startswith("no match:"))

    def test_path_between_files(self):
        found = queries.path_between(self.graph, "app/main.py", "tools.py")
        self.assertEqual(found[-1], "1 hops")

    def test_budget_cuts_output(self):
        self.assertEqual(len(queries.find(self.graph, ["compute", "orphan"], 10)), 2)


if __name__ == "__main__":
    unittest.main()
