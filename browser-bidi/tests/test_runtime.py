import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import bidi
from actions import tabs
from core import browser, common, processes, session
from core.wsclient import WebSocket


class TabChoiceTest(unittest.TestCase):
    contexts = [{"context": "a"}, {"context": "b"}]

    def test_explicit_tab_wins(self):
        self.assertEqual(bidi.tab_index(self.contexts, 0, "b"), 0)

    def test_tab_of_the_last_nav_is_used(self):
        self.assertEqual(bidi.tab_index(self.contexts, None, "b"), 1)

    def test_gone_or_missing_tab_falls_back_to_zero(self):
        self.assertEqual((bidi.tab_index(self.contexts, None, "z"), bidi.tab_index(self.contexts, None, None)), (0, 0))

    def test_remember_tab_keeps_the_session_state(self):
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / "bidi-9300.session"
            with mock.patch.object(session, "state_file", lambda port: state):
                session.remember_tab(9300, "b")
                self.assertFalse(state.exists())
                state.write_text('{"ws": "ws://x", "session": "s"}')
                session.remember_tab(9300, "b")
                self.assertEqual(session.read_state(9300), {"ws": "ws://x", "session": "s", "tab": "b"})

    def test_reconnect_keeps_the_remembered_tab(self):
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / "bidi-9300.session"
            state.write_text('{"ws": "ws://old", "session": "s", "tab": "b"}')
            created = {"value": {"sessionId": "n", "capabilities": {"webSocketUrl": "ws://new"}}}
            with mock.patch.object(session, "state_file", lambda port: state), \
                    mock.patch.object(session, "WORK_DIR", Path(folder)), \
                    mock.patch.object(session, "http_json", return_value=created), \
                    mock.patch.object(session, "WebSocket", side_effect=[OSError(), mock.Mock()]):
                session.open_session(9300)
                self.assertEqual(session.read_state(9300)["tab"], "b")

    def test_newtab_remembers_the_created_tab(self):
        page = mock.Mock(value="", options=mock.Mock(port=9300))
        page.call.return_value = {"context": "c"}
        with mock.patch.object(tabs, "remember_tab") as remember, mock.patch.object(tabs, "tree", return_value=[]), \
                mock.patch.object(tabs, "index_of", return_value=1), mock.patch("builtins.print"):
            tabs.newtab(page)
        remember.assert_called_once_with(9300, "c")


class CloseTest(unittest.TestCase):
    def stop(self, gone, drivers, folder):
        with mock.patch.object(browser, "open_session", side_effect=ConnectionRefusedError()), \
                mock.patch.object(browser, "state_file", lambda port: Path(folder) / "s"), \
                mock.patch.object(browser, "wait_gone", return_value=gone), \
                mock.patch.object(browser, "own_driver", side_effect=drivers), \
                mock.patch.object(browser, "own_browser", return_value=[]), \
                mock.patch.object(browser, "kill", side_effect=lambda entries: [e["ProcessId"] for e in entries]):
            return browser.stop(9300)

    def test_stop_cleans_up_when_the_driver_is_dead(self):
        with tempfile.TemporaryDirectory() as folder:
            line = self.stop([{"ProcessId": 7}], [[{"ProcessId": 8}], []], folder)
        self.assertEqual(line, "browser closed, port 9300 released, forced pids [7], driver pids [8] stopped, "
                               "nothing left")

    def test_stop_lists_what_survived(self):
        with tempfile.TemporaryDirectory() as folder:
            line = self.stop([], [[], [{"ProcessId": 8}]], folder)
        self.assertTrue(line.endswith(", pids [8] still running"))

    def test_close_skips_the_port_check_and_the_session(self):
        with mock.patch.object(sys, "argv", ["bidi.py", "close", "--port", "9300"]), \
                mock.patch.object(bidi, "stop", return_value="done") as stop, \
                mock.patch.object(bidi, "port_free", side_effect=AssertionError), \
                mock.patch.object(bidi, "open_session", side_effect=AssertionError), \
                mock.patch("builtins.print"):
            bidi.main()
        stop.assert_called_once_with(9300)


class FreePortTest(unittest.TestCase):
    def test_port_is_reserved_by_its_profile_folder(self):
        with tempfile.TemporaryDirectory() as folder, \
                mock.patch.object(common, "WORK_DIR", Path(folder)), \
                mock.patch.object(common, "port_free", return_value=True), \
                mock.patch.object(common.random, "randrange", return_value=0):
            self.assertEqual((common.free_port(), common.free_port("firefox")), (9300, 9301))
            self.assertTrue((Path(folder) / "chrome-9300").is_dir())
            self.assertTrue((Path(folder) / "firefox-9301").is_dir())


class ProcessMatchTest(unittest.TestCase):
    table = [{"ProcessId": 1, "CommandLine": "chrome.exe --remote-debugging-port=9300 --user-data-dir=x"},
             {"ProcessId": 2, "CommandLine": "chrome.exe --remote-debugging-port=93000"},
             {"ProcessId": 3, "CommandLine": "chrome.exe --remote-debugging-port=930"},
             {"ProcessId": 4, "CommandLine": "chrome.exe --type=renderer --remote-debugging-port=9300"},
             {"ProcessId": 5, "CommandLine": None},
             {"ProcessId": 6, "CommandLine": "chromedriver.exe --port=10300"}]

    def test_only_the_main_process_of_the_port_matches(self):
        with mock.patch.object(processes, "process_table", return_value=self.table):
            self.assertEqual([entry["ProcessId"] for entry in processes.own_browser(9300)], [1])
            self.assertEqual([entry["ProcessId"] for entry in processes.own_driver(9300)], [6])


class FakeSocket:
    def __init__(self, data):
        self.data = data

    def settimeout(self, seconds):
        pass

    def recv(self, size):
        chunk, self.data = self.data[:size], self.data[size:]
        return chunk


class ReadFrameTest(unittest.TestCase):
    def read(self, header, payload):
        socket = WebSocket.__new__(WebSocket)
        socket.sock, socket.buffer, socket.parts = FakeSocket(header + payload + b"\x81\x01z"), bytearray(), []
        return socket, socket.read_frame(float("inf"))

    def test_eight_byte_length_frame(self):
        payload = b"a" * 70000
        socket, frame = self.read(b"\x81\x7f" + (70000).to_bytes(8, "big"), payload)
        self.assertEqual(frame, (0x80, 1, payload))
        self.assertEqual(socket.read_frame(float("inf"))[2], b"z")

    def test_two_byte_length_frame(self):
        payload = b"b" * 300
        _, frame = self.read(b"\x81\x7e" + (300).to_bytes(2, "big"), payload)
        self.assertEqual(frame, (0x80, 1, payload))


if __name__ == "__main__":
    unittest.main()
