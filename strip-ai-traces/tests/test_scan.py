import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "lib"))

import gitlog
import scan
from files import walk
from markdown import quoted


class GitTest(unittest.TestCase):
    def test_a_failed_git_log_is_not_a_clean_history(self):
        failed = (None, "", "git timed out after 60 s")
        with mock.patch.object(gitlog, "run", return_value=failed):
            with self.assertRaises(gitlog.GitError):
                gitlog.history(Path("."))
            report = scan.Report(Path(".").resolve(), True)
            scan.scan_git(Path(".").resolve(), report)
        rows = [row for _, row in report.rows]
        self.assertEqual(rows, [". by hand: history not read: git rev-list: git timed out after 60 s"])


class ScanTest(unittest.TestCase):
    def test_a_parent_folder_named_lang_does_not_hide_the_scan(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp, "lang", "proj")
            project.mkdir(parents=True)
            (project / "README.md").write_text("It is crucial.\n", encoding="utf-8")
            report = scan.Report(project.resolve(), False)
            scan.scan_file((project / "README.md").resolve(), report, False, project.resolve())
        self.assertEqual([row for _, row in report.rows], ["README.md:1 by hand: vocabulary: crucial"])

    def test_walk_never_enters_skipped_folders(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "node_modules" / "pkg").mkdir(parents=True)
            (base / "node_modules" / "pkg" / "a.md").write_text("x", encoding="utf-8")
            (base / "b.md").write_text("x", encoding="utf-8")
            self.assertEqual([path.name for path in walk(base)], ["b.md"])

    def test_quoted_lines_are_skipped_only_inside_a_closed_region(self):
        lines = ["<!-- scan: off -->", "delve", "<!-- scan: on -->", "delve"]
        self.assertEqual(quoted(lines), {2})
        self.assertEqual(quoted(["<!-- scan: off -->", "delve"]), set())
        report = scan.Report(Path(".").resolve(), False)
        scan._prose(Path("x.md"), "\n".join(lines) + "\n", report, False)
        self.assertEqual([row for _, row in report.rows], ["x.md:4 by hand: vocabulary: delve"])

    def test_a_signature_inside_code_is_a_flag(self):
        report = scan.Report(Path(".").resolve(), False)
        scan._code(Path("a.py"), "code", 'EMAIL = "noreply@anthropic.com"\n', report)
        self.assertEqual([row for _, row in report.rows],
                         ["a.py:1 flag: signature: noreply@anthropic.com (a string stays, a comment is fixed)"])

    def test_a_signature_in_a_code_comment_is_by_hand(self):
        report = scan.Report(Path(".").resolve(), False)
        scan._code(Path("a.py"), "code", "# Generated with Claude Code\n", report)
        self.assertEqual([row for _, row in report.rows], ["a.py:1 by hand: signature: generated with claude"])

    def test_a_value_folder_target_keeps_its_own_name(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp, "site", "translations")
            folder.mkdir(parents=True)
            (folder / "fr.md").write_text("It is crucial.\n", encoding="utf-8")
            for target in (folder, folder / "fr.md"):
                output = io.StringIO()
                with mock.patch.object(sys, "argv", ["scan.py", str(target), "--no-git"]), redirect_stdout(output):
                    scan.main()
                self.assertEqual(output.getvalue().splitlines()[-1], "0 fixed, 0 to fix by hand, 0 flagged")

    def test_target_order_does_not_change_the_total(self):
        with tempfile.TemporaryDirectory() as temp:
            first, second = Path(temp, "a"), Path(temp, "lang", "b")
            for folder in (first, second):
                folder.mkdir(parents=True)
                (folder / "README.md").write_text("It is crucial.\n", encoding="utf-8")
            totals = []
            for order in ([first, second], [second, first]):
                output = io.StringIO()
                argv = ["scan.py", *map(str, order), "--no-git"]
                with mock.patch.object(sys, "argv", argv), redirect_stdout(output):
                    scan.main()
                totals.append(output.getvalue().splitlines()[-1])
        self.assertEqual(totals, ["0 fixed, 2 to fix by hand, 0 flagged"] * 2)

    def test_several_targets_give_one_total(self):
        with tempfile.TemporaryDirectory() as temp:
            first, second = Path(temp, "a.md"), Path(temp, "b.md")
            first.write_text("It is crucial.\n", encoding="utf-8")
            second.write_text("We delve.\n", encoding="utf-8")
            output = io.StringIO()
            argv = ["scan.py", str(first), str(second), str(first), "--no-git"]
            with mock.patch.object(sys, "argv", argv), redirect_stdout(output):
                scan.main()
        lines = output.getvalue().splitlines()
        self.assertEqual(lines[-1], "0 fixed, 2 to fix by hand, 0 flagged")
        self.assertEqual(len(lines), 3)


if __name__ == "__main__":
    unittest.main()
