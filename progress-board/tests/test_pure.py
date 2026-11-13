import http.client
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import server
import store

TIMEOUT = 10


class Board(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="progress-board-test-")
        self.saved = store.STATE
        store.STATE = Path(self.temp.name) / ".state.json"
        store.state = {"projects": [], "known": {}, "cfg": dict(store.DEFAULTS)}
        store.listeners.clear()

    def tearDown(self):
        store.STATE = self.saved
        self.temp.cleanup()

    def history(self, name):
        project = next(p for p in store.state["projects"] if p["name"] == name)
        return [(point["v"], point["s"]) for point in project["history"]]


class StoreTest(Board):
    def test_a_line_starts_at_zero_and_ignores_a_second_100(self):
        store.update("a", 40, "tests", 1000)
        store.update("a", 100, "", 1010)
        store.update("a", 100, "", 1020)
        self.assertEqual(self.history("a"), [(0, ""), (40, "tests"), (100, "")])
        self.assertEqual(store.state["projects"][0]["step"], "tests")

    def test_a_late_100_after_leaving_is_dropped(self):
        store.update("a", 100, "", 1000)
        store.update("a", 100, "", 1000 + store.HOUR + 1)
        self.assertEqual(store.state["projects"], [])
        store.update("a", 10, "", 1000 + store.HOUR + 2)
        self.assertEqual(self.history("a"), [(0, ""), (10, "")])

    def test_prune_uses_done_for_finished_and_idle_for_the_rest(self):
        store.update("done", 100, "", 1000)
        store.update("busy", 50, "", 1000)
        self.assertTrue(store.prune(1000 + store.HOUR + 1))
        self.assertEqual([p["name"] for p in store.state["projects"]], ["busy"])
        self.assertTrue(store.prune(1000 + 3 * store.DAY + 1))
        self.assertEqual((store.state["projects"], store.state["known"]), ([], {}))

    def test_trimming_keeps_the_start(self):
        store.update("a", 1, "", 1000)
        for second in range(store.MAX_POINTS + 10):
            store.update("a", 2, "", 1001 + second)
        history = store.state["projects"][0]["history"]
        self.assertEqual((len(history), history[0]["v"]), (store.MAX_POINTS, 0))

    def test_a_returning_name_gets_its_color_and_icon_back(self):
        for name in "abcdefgh":
            store.update(name, 10, "", 1000)
        icons = {p["icon"] for p in store.state["projects"]}
        self.assertEqual(len(icons), len(store.ICONS))
        before = next(p for p in store.state["projects"] if p["name"] == "c")
        store.admin("/_del/c", "")
        store.state["known"]["c"] = [before["slot"], before["icon"], False, 1000]
        again = store.new_project("c")
        self.assertEqual((again["slot"], again["icon"]), (before["slot"], before["icon"]))

    def test_save_replaces_the_file_whole(self):
        store.update("a", 40, "", 1000)
        self.assertEqual([path.name for path in Path(self.temp.name).iterdir()], [".state.json"])
        self.assertEqual(store.load()["projects"][0]["name"], "a")

    def test_save_survives_a_locked_state_file(self):
        real = Path.replace
        fails = iter([True])
        def replace(path, target):
            if next(fails, False):
                raise PermissionError(5, "Access is denied")
            return real(path, target)
        with mock.patch.object(Path, "replace", replace):
            store.update("a", 40, "", 1000)
        self.assertEqual(store.load()["projects"][0]["name"], "a")
        with mock.patch.object(Path, "replace", side_effect=PermissionError), mock.patch.object(store.time, "sleep"):
            store.update("b", 10, "", 1010)
        self.assertEqual([path.name for path in Path(self.temp.name).iterdir()], [".state.json"])
        self.assertEqual([p["name"] for p in store.load()["projects"]], ["a", "b"])


class ServerTest(Board):
    def setUp(self):
        super().setUp()
        self.server = server.serve(0)
        self.port = self.server.server_port
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        super().tearDown()

    def ask(self, method, path, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=TIMEOUT)
        try:
            connection.request(method, path, headers=headers or {})
            return connection.getresponse().status
        finally:
            connection.close()

    def test_agents_report_and_other_sites_are_refused(self):
        self.assertEqual(self.ask("GET", "/a/50/tests"), 200)
        self.assertEqual(self.ask("GET", "/", {"Sec-Fetch-Site": "cross-site"}), 200)
        self.assertEqual(self.ask("GET", "/b/50", {"Sec-Fetch-Site": "cross-site"}), 403)
        self.assertEqual(self.ask("GET", "/b/50", {"Origin": "http://evil.example"}), 403)
        rebound = {"Host": f"evil.example:{self.port}", "Origin": f"http://evil.example:{self.port}"}
        self.assertEqual(self.ask("GET", "/", rebound), 403)
        self.assertEqual(self.ask("POST", "/_clear", rebound), 403)
        self.assertEqual([p["name"] for p in store.state["projects"]], ["a"])

    def test_a_second_server_on_the_same_port_fails(self):
        with self.assertRaises(OSError):
            server.serve(self.port).server_close()

    def test_assets_stay_inside_the_site_folder(self):
        self.assertIsNone(server.built_file("/assets/../server.py"))
        self.assertIsNone(server.built_file("/assets/%2e%2e/%2e%2e/server.py"))
        asset = next((store.PAGE.parent / "assets").iterdir())
        self.assertEqual(server.built_file(f"/assets/{asset.name}"), asset.resolve())


if __name__ == "__main__":
    unittest.main()
