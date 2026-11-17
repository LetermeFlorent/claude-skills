import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path[:0] = [str(SCRIPTS / "lib"), str(SCRIPTS)]

import findings
import scan
from parsers import HIGH, MEDIUM, SECRET, Raw
from project import TEMPORARY, is_test

SQL_LINE = "query = 'a' + name"


def raw(tool="bandit", line=2, level=MEDIUM, topic="89"):
    return Raw(tool, f"{tool}-rule", level, "app.py", line, "possible injection", topic)


def item(key, path, level=HIGH, **extra):
    return {"key": key, "path": path, "line": 1, "level": level, "topic": "89", "tools": ["semgrep"], "ids": ["r"],
            "message": "m", **extra}


def entry(blocking, ran=1, passed=3, failed=0):
    return {"blocking": blocking, "ran": ran, "passed": passed, "failed": failed}


class Merge(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name).resolve()
        (self.root / "app.py").write_text(f"x = 1\n{SQL_LINE}\n{SQL_LINE}\n", encoding="utf-8")

    def tearDown(self):
        self.folder.cleanup()

    def test_two_tools_on_one_line_merge_and_the_cwe_floor_raises_them(self):
        found = findings.merge([raw(), raw("semgrep")._replace(path=str(self.root / "app.py"))], self.root)
        self.assertEqual([(one["level"], one["tools"]) for one in found], [(HIGH, ["bandit", "semgrep"])])

    def test_same_text_twice_gets_a_numbered_key(self):
        first, second = findings.merge([raw(line=2), raw(line=3)], self.root)
        self.assertEqual(second["key"], first["key"] + "#2")

    def test_key_survives_a_line_shift(self):
        before = findings.merge([raw(line=2)], self.root)[0]["key"]
        (self.root / "app.py").write_text(f"\n\nx = 1\n{SQL_LINE}\n", encoding="utf-8")
        self.assertEqual(findings.merge([raw(line=4)], self.root)[0]["key"], before)

    def test_ids_joined_by_a_tool_are_split_and_deduplicated(self):
        found = findings.merge([raw("npm-audit", line=0, topic="package:x")._replace(ident="B,A"),
                                raw("osv", line=0, topic="package:x")._replace(ident="A")], self.root)
        self.assertEqual(found[0]["ids"], ["A", "B"])

    def test_paths_from_windows_tools_become_project_paths(self):
        self.assertEqual(findings.relative_path(".\\src\\a.py", self.root), "src/a.py")
        self.assertEqual(findings.relative_path("", self.root), findings.NO_PATH)

    def test_history_secrets_stay_apart(self):
        found = findings.merge_all([raw("gitleaks", level=SECRET, topic="798"),
                                    raw("gitleaks-history", level=SECRET, topic="798")], self.root)
        self.assertEqual([one.get("history", False) for one in found], [False, True])


class Split(unittest.TestCase):
    def test_each_finding_lands_in_one_bucket(self):
        found = [item("a", "a.py"), item("b", "b.py"), item("c", "a.py"), item("d", "node_modules/x.js"),
                 item("e", "tests/test_secureloop_tmp_x.py"), item("f", "-"), item("g", "a.py", history=True)]
        buckets = findings.split(found, {"a.py"}, {"a.py", "b.py"}, {"c": "reason"})
        self.assertEqual({name: [one["key"] for one in items] for name, items in buckets.items() if items},
                         {"scope": ["a"], "elsewhere": ["b", "f"], "dismissed": ["c"], "ignored": ["d"],
                          "temporary": ["e"], "revoke": ["g"]})

    def test_rows_put_fixes_first_and_hide_low_findings_elsewhere(self):
        buckets = findings.split([item("a", "a.py", MEDIUM), item("b", "a.py"), item("c", "b.py"),
                                  item("d", "b.py", MEDIUM), item("e", "a.py", history=True)], {"a.py"},
                                 {"a.py", "b.py"}, {})
        self.assertEqual([line.split(":")[0] for line in scan.rows(buckets)], ["fix", "revoke", "also", "elsewhere"])


class Ledgers(unittest.TestCase):
    def test_false_positive_without_reason_is_not_applied(self):
        accepted, bad = findings.false_positives(["abc the value is a constant", "def"])
        self.assertEqual((list(accepted), len(bad)), (["abc"], 1))

    def test_advisory_lines(self):
        entries, bad = findings.advisories(["open HIGH CVE-1 package.json : known flaw", "not-applicable high X-2 - :",
                                            "fixed urgent X-3 - : bumped", "open high X-4 gone.txt : x", "nonsense"],
                                           {"package.json"})
        self.assertEqual(([one["id"] for one in entries], len(bad)), (["CVE-1"], 4))
        self.assertEqual(findings.advisory_raws(entries)[0][:5], ("advisory", "CVE-1", HIGH, "package.json", 0))


class Decide(unittest.TestCase):
    def test_stop_rules(self):
        self.assertEqual(scan.decide([entry(2), entry(0)]), (scan.STOP, "clean"))
        self.assertEqual(scan.decide([entry(0, ran=0)]), (scan.STOP, "no scanner ran"))
        self.assertTrue(scan.decide([entry(3), entry(3), entry(4)])[1].startswith("stalled"))
        self.assertTrue(scan.decide([entry(5), entry(4), entry(3), entry(2), entry(1)])[1].startswith("limit"))

    def test_keep_going(self):
        self.assertEqual(scan.decide([entry(5), entry(3), entry(5)])[0], scan.CONTINUE)
        self.assertIn("tests worse", scan.decide([entry(2), entry(0, failed=1)])[1])
        self.assertEqual(scan.decide([entry(2), entry(0, passed=2)])[0], scan.CONTINUE)
        self.assertEqual(scan.decide([entry(2), {**entry(0), "touched": 1}]),
                         (scan.CONTINUE, "0 blocking in scope, old tests touched"))

    def test_bloat(self):
        self.assertTrue(scan.bloat_lines(100, 140)[-1].startswith("bloat:"))
        self.assertEqual(len(scan.bloat_lines(100, 120)), 1)
        self.assertIn("none at start", scan.bloat_lines(0, 10)[0])


class Names(unittest.TestCase):
    def test_temporary_and_test_names(self):
        for name in ("tests/test_secureloop_tmp_sql.py", "src/SecureLoopTmp_PathTest.java",
                     "web/secureloop-tmp-ssrf.test.ts", "pkg/x_secureloop_tmp_test.go"):
            self.assertTrue(TEMPORARY.search(name), name)
            self.assertFalse(is_test(name), name)
        self.assertTrue(all(map(is_test, ("tests/test_app.py", "src/app.spec.ts", "pkg/a_test.go"))))
        self.assertFalse(TEMPORARY.search("tests/test_secure_loop.py") or is_test("src/app.py"))


if __name__ == "__main__":
    unittest.main()
