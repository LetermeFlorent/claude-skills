import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

from common import ENCODING, temp_root
from server import Companion
from session import CHOICES, LOG, SCREENS

KEY = "test-key"
SPEC_TEXT = "# Prets de livres\n\n## But\n\nSavoir qui a quel livre.\n"
SPEC_NAME = "2026-10-22-book-loans-design.md"


def scratch():
    temp_root().mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=temp_root())


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.temp = scratch()
        self.folder = Path(self.temp.name)
        (self.folder / SCREENS).mkdir()
        self.server = Companion(self.folder, KEY)
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def loop(self):
        while not self.server.stopping:
            self.server.handle_request()

    def tearDown(self):
        self.call("/stop", b"")
        self.thread.join(5)
        self.server.server_close()
        self.temp.cleanup()

    def call(self, route, data=None, key=KEY):
        address = f"http://127.0.0.1:{self.server.server_address[1]}{route}"
        request = urllib.request.Request(address, data=data, headers={"X-Key": key} if key else {})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(request, timeout=5) as answer:
                return answer.status, answer.read().decode(ENCODING), answer.headers.get("Set-Cookie")
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode(ENCODING), error.headers.get("Set-Cookie")

    def test_the_key_is_required(self):
        status, body, cookie = self.call("/", key=None)
        self.assertEqual(status, 403)
        self.assertIn("Adresse incomplète", body)
        self.assertIsNone(cookie)
        self.assertEqual(self.call("/?key=wrong", key=None)[0], 403)

    def test_waiting_then_fragment(self):
        status, body, cookie = self.call("/")
        self.assertEqual(status, 200)
        self.assertIn("Rien à montrer", body)
        self.assertIn(KEY, cookie)
        (self.folder / SCREENS / "layout.html").write_text("<h1>Quelle mise en page ?</h1>", encoding=ENCODING)
        body = self.call("/")[1]
        self.assertIn("Quelle mise en page ?", body)
        self.assertIn("Envoyer mes choix", body)
        self.assertTrue(self.call("/version")[1].startswith("layout.html:"))

    def test_full_document_is_served_as_it_is(self):
        page = "<!doctype html><html><body>plein</body></html>"
        (self.folder / SCREENS / "full.html").write_text(page, encoding=ENCODING)
        self.assertEqual(self.call("/")[1], page)

    def test_choice_is_recorded_and_logged(self):
        payload = {"screen": "layout.html", "selected": {"mise": ["b"]}, "note": "", "sent": True}
        self.assertEqual(self.call("/choice", json.dumps(payload).encode(ENCODING))[0], 200)
        saved = json.loads((self.folder / CHOICES).read_text(encoding=ENCODING))
        self.assertEqual(saved["layout.html"]["selected"], {"mise": ["b"]})
        self.assertIn("sent layout.html", (self.folder / LOG).read_text(encoding=ENCODING))
        self.assertEqual(self.call("/choice", b"not json")[0], 400)

    def test_files_stay_inside_the_screens_folder(self):
        (self.folder / SCREENS / "pic.txt").write_text("image", encoding=ENCODING)
        self.assertEqual(self.call("/files/pic.txt")[1], "image")
        self.assertIn("Rien à montrer", self.call("/")[1])
        self.assertEqual(self.call("/files/../server.log")[0], 404)
        self.assertEqual(self.call("/files/%2e%2e%2fserver.log")[0], 404)


class SpecCheckTest(unittest.TestCase):
    def setUp(self):
        self.temp = scratch()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.spec = self.root / ".ia" / "specs" / SPEC_NAME
        self.spec.parent.mkdir(parents=True)
        self.spec.write_text(SPEC_TEXT, encoding=ENCODING)

    def tearDown(self):
        self.temp.cleanup()

    def check(self, path):
        done = subprocess.run([sys.executable, "-I", str(SCRIPTS / "spec_check.py"), str(path)],
                              capture_output=True, text=True, encoding=ENCODING)
        return done.returncode, done.stdout

    def test_good_spec_adds_the_exclude_once(self):
        code, out = self.check(self.spec)
        self.assertEqual(code, 0, out)
        self.assertIn("added .ia/", out)
        self.assertIn(".ia/", (self.root / ".git" / "info" / "exclude").read_text(encoding=ENCODING))
        code, out = self.check(self.spec)
        self.assertEqual(code, 0, out)
        self.assertNotIn("added", out)

    def test_placeholder_and_tracked_spec_are_refused(self):
        self.spec.write_text(SPEC_TEXT + "\n## Rappel\n\nDelai TBD.\n", encoding=ENCODING)
        subprocess.run(["git", "-C", str(self.root), "add", "-f", str(self.spec)], check=True)
        code, out = self.check(self.spec)
        self.assertEqual(code, 2)
        self.assertIn("placeholder", out)
        self.assertIn("is tracked by git", out)

    def test_spec_outside_ia_is_refused(self):
        other = self.root / "docs" / "specs" / SPEC_NAME
        other.parent.mkdir(parents=True)
        other.write_text(SPEC_TEXT, encoding=ENCODING)
        code, out = self.check(other)
        self.assertEqual(code, 2)
        self.assertIn("is not in", out)


if __name__ == "__main__":
    unittest.main()
