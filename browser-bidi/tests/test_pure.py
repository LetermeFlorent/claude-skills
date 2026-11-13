import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import launch
import measure_images
from actions import inputs, reading
from core.common import driver_port, profile_dir, split_value
from core.driver import build_of, write_firefox_prefs
from actions.forms import literal
from actions.page import flatten, index_of, locator, plain
from core.wsclient import apply_mask


class CommonTest(unittest.TestCase):
    def test_split_value_pads_missing_parts(self):
        self.assertEqual(split_value("a", 2), ["a", ""])

    def test_split_value_keeps_the_rest_in_the_last_part(self):
        self.assertEqual(split_value("a|b|c", 2), ["a", "b|c"])

    def test_driver_port_adds_the_offset(self):
        self.assertEqual(driver_port(9300), 10300)

    def test_build_of_keeps_three_fields(self):
        self.assertEqual(build_of("120.0.6099.109"), "120.0.6099")

    def test_profile_name_carries_the_browser(self):
        self.assertEqual((profile_dir(9300).name, profile_dir(9300, "firefox").name), ("chrome-9300", "firefox-9300"))

    def test_firefox_prefs_are_user_pref_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            profile = Path(folder) / "firefox-9300"
            write_firefox_prefs(profile)
            lines = (profile / "user.js").read_text(encoding="utf-8").splitlines()
        self.assertIn('user_pref("marionette.port", 0);', lines)
        self.assertTrue(all(line.startswith("user_pref(") and line.endswith(");") for line in lines))


class SharedTest(unittest.TestCase):
    def test_plain_unwraps_arrays_and_objects(self):
        remote = {"type": "object", "value": [["key", {"type": "array", "value": [{"type": "number", "value": 3}]}]]}
        self.assertEqual(plain(remote), {"key": [3]})

    def test_plain_names_the_type_of_valueless_remotes(self):
        self.assertEqual(plain({"type": "null"}), "null")

    def test_flatten_walks_children_depth_first(self):
        tree = [{"context": "a", "children": [{"context": "b", "children": []}]}, {"context": "c"}]
        self.assertEqual([entry["context"] for entry in flatten(tree)], ["a", "b", "c"])

    def test_index_of_returns_minus_one_when_missing(self):
        contexts = [{"context": "a"}, {"context": "b"}]
        self.assertEqual((index_of(contexts, "b"), index_of(contexts, "z")), (1, -1))

    def test_locator_guesses_xpath_from_the_first_character(self):
        self.assertEqual(locator("//div")["type"], "xpath")
        self.assertEqual(locator("div.a")["type"], "css")
        self.assertEqual(locator("//div", "css")["type"], "css")


class XpathLiteralTest(unittest.TestCase):
    def test_plain_text_is_single_quoted(self):
        self.assertEqual(literal("abc"), "'abc'")

    def test_text_with_apostrophe_is_double_quoted(self):
        self.assertEqual(literal("a'b"), '"a\'b"')

    def test_text_with_both_quotes_uses_concat(self):
        self.assertEqual(literal("a'\"b"), "concat('a', \"'\", '\"b')")


class WebSocketMaskTest(unittest.TestCase):
    def test_mask_is_its_own_inverse(self):
        key = b"\x01\x02\x03\x04"
        payload = b"hello world"
        self.assertEqual(apply_mask(apply_mask(payload, key), key), payload)

    def test_empty_payload_stays_empty(self):
        self.assertEqual(apply_mask(b"", b"abcd"), b"")


class ParsingTest(unittest.TestCase):
    def test_size_of_reads_width_and_height(self):
        self.assertEqual(launch.size_of("390X844"), (390, 844))

    def test_widths_of_skips_blanks(self):
        self.assertEqual(measure_images.widths_of("390, 1440,,"), [390, 1440])

    def test_coordinates_accept_comma_and_x(self):
        self.assertEqual((inputs.coordinates("10,20"), inputs.coordinates("10x20")), ((10, 20), (10, 20)))


class ReadingTest(unittest.TestCase):
    def test_describe_prints_console_entries(self):
        event = {"method": "log.entryAdded", "params": {"level": "warn", "text": "boom"}}
        self.assertEqual(reading.describe(event, False), "[warn] boom")

    def test_describe_hides_successful_requests_unless_asked(self):
        event = {"method": "network.responseCompleted",
                 "params": {"response": {"status": 200}, "request": {"method": "GET", "url": "http://x"}}}
        self.assertIsNone(reading.describe(event, False))
        self.assertEqual(reading.describe(event, True), "200 GET http://x")

    def test_describe_shows_failed_requests(self):
        event = {"method": "network.fetchError", "params": {"errorText": "net::ERR", "request": {"url": "http://x"}}}
        self.assertEqual(reading.describe(event, False), "FAILED net::ERR http://x")


if __name__ == "__main__":
    unittest.main()
