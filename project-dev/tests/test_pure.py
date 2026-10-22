import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))

from gitrepo import has_exclude
from images import kind, size_text
from index import TO_DESCRIBE, entries, problems, with_lines
from references import sources, target

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", 1280, 800) + b"\x08\x02\x00\x00\x00"
GIF = b"GIF89a" + struct.pack("<HH", 64, 32) + b"\x00" * 6
BMP = b"BM" + b"\x00" * 16 + struct.pack("<ii", 300, -200) + b"\x00" * 8
JPEG = (b"\xff\xd8" + b"\xff\xe0" + struct.pack(">H", 4) + b"\x00\x00"
        + b"\xff\xc0" + struct.pack(">HBHH", 11, 8, 480, 640) + b"\x00" * 6)
WEBP = (b"RIFF" + b"\x00" * 4 + b"WEBP" + b"VP8X" + b"\x00" * 8
        + (1023).to_bytes(3, "little") + (767).to_bytes(3, "little"))
SVG = b'<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40"></svg>'


class KindTest(unittest.TestCase):
    def test_formats_and_sizes(self):
        self.assertEqual(kind(PNG), ("png", (1280, 800)))
        self.assertEqual(kind(GIF), ("gif", (64, 32)))
        self.assertEqual(kind(BMP), ("bmp", (300, 200)))
        self.assertEqual(kind(JPEG), ("jpeg", (640, 480)))
        self.assertEqual(kind(WEBP), ("webp", (1024, 768)))
        self.assertEqual(kind(SVG), ("svg", (120, 40)))

    def test_text_is_not_an_image(self):
        self.assertEqual(kind(b"Maquette finale, voir le PDF"), (None, None))

    def test_size_text(self):
        self.assertEqual(size_text((1280, 800)), "1280x800")
        self.assertEqual(size_text(None), "size unknown")


class IndexTest(unittest.TestCase):
    def test_new_index_gets_header_and_lines(self):
        text = with_lines("", ["accueil.png", "palette.png"])
        self.assertTrue(text.startswith("# Références"))
        self.assertEqual(entries(text), {"accueil.png": TO_DESCRIBE, "palette.png": TO_DESCRIBE})

    def test_known_line_is_kept(self):
        text = with_lines("", ["accueil.png"]).replace(TO_DESCRIBE, "bandeau vert #1b5e20")
        again = with_lines(text, ["accueil.png", "logo.svg"])
        self.assertEqual(entries(again)["accueil.png"], "bandeau vert #1b5e20")
        self.assertIn("- accueil.png : bandeau vert #1b5e20\n- logo.svg : ", again)

    def test_new_line_goes_before_the_no_file_section(self):
        text = "# Références\n\n- a.png : vert\n\n## Sans fichier\n\n- capture collée : menu\n"
        result = with_lines(text, ["b.png"])
        self.assertLess(result.index("- b.png"), result.index("## Sans fichier"))
        self.assertNotIn("capture collée", entries(result))

    def test_problems_name_each_gap(self):
        text = "- a.png : vert\n- b.png : (à décrire)\n- gone.png : rouge\n"
        found = problems(text, {"a.png": "png", "b.png": "png", "c.png": "png", "notes.txt": None})
        self.assertEqual(found, [
            "write in references.md what to take from b.png",
            "c.png has no line in references.md",
            "notes.txt is not an image: move it out of the references folder",
            "references.md names gone.png, which is not in the folder",
        ])

    def test_complete_index_has_no_problem(self):
        self.assertEqual(problems("- a.png : vert\n", {"a.png": "png"}), [])


class SourcesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_folder_keeps_images_and_skips_the_rest(self):
        shots = self.root / "maquettes"
        shots.mkdir()
        (shots / "accueil.png").write_bytes(PNG)
        (shots / "lisez-moi.txt").write_text("notes", encoding="utf-8")
        found, skipped, missing = sources([str(shots), str(self.root / "absent.png")])
        self.assertEqual([p.name for p in found], ["accueil.png"])
        self.assertEqual([p.name for p in skipped], ["lisez-moi.txt"])
        self.assertEqual([p.name for p in missing], ["absent.png"])

    def test_same_name_other_content_gets_a_number(self):
        folder, source = self.root / "refs", self.root / "accueil.png"
        folder.mkdir()
        source.write_bytes(PNG)
        (folder / "accueil.png").write_bytes(GIF)
        self.assertEqual(target(folder, source).name, "accueil-2.png")
        (folder / "accueil.png").write_bytes(PNG)
        self.assertEqual(target(folder, source).name, "accueil.png")


class ExcludeTest(unittest.TestCase):
    def test_forms(self):
        self.assertTrue(has_exclude("node_modules\n/.ia/\n"))
        self.assertFalse(has_exclude("node_modules\n.idea/\n"))


if __name__ == "__main__":
    unittest.main()
