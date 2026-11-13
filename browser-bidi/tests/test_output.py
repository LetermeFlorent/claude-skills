import io
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import measure_images
import visual_test
from actions import capture, reading
from core import target
from core.driver import unzip_to


class ImageVerdictTest(unittest.TestCase):
    def verdict(self, natural_width):
        return visual_test.verdict({"box": [100, 50], "dpr": 2, "natural": [natural_width, 10]})

    def test_missing_file_is_not_loaded(self):
        self.assertEqual(self.verdict(0), "not loaded")

    def test_small_file_is_blurry(self):
        self.assertEqual(self.verdict(100), "blurry, file 0.50x of the box")

    def test_large_file_is_heavy(self):
        self.assertEqual(self.verdict(500), "heavy, file 2.50x of the box")

    def test_fitting_file_is_fine(self):
        self.assertIsNone(self.verdict(300))

    def test_single_density_file_is_blurry_at_phone_width(self):
        record = {"box": [390, 200], "dpr": measure_images.dpr_for(390), "natural": [390, 200]}
        self.assertEqual(visual_test.verdict(record), "blurry, file 0.33x of the box")

    def test_triple_density_file_is_fine_at_phone_width(self):
        record = {"box": [390, 200], "dpr": measure_images.dpr_for(390), "natural": [1170, 600]}
        self.assertIsNone(visual_test.verdict(record))

    def test_desktop_width_gets_double_density(self):
        self.assertEqual((measure_images.dpr_for(480), measure_images.dpr_for(1440)), (3, 2))

    def test_measure_width_sets_the_density(self):
        calls = []
        answer = {"type": "success", "result": {"value": '{"dpr": 3, "images": []}'}}
        fake = SimpleNamespace(call=lambda method, params, *rest: calls.append(params) or answer)
        measure_images.measure_width(fake, "ctx", "http://x", (390, 720))
        self.assertEqual(calls[0]["devicePixelRatio"], 3)


class ShotScaleTest(unittest.TestCase):
    def test_small_capture_is_kept(self):
        self.assertEqual(capture.scale_of(800, 600), 1.0)

    def test_wide_capture_fits_1024(self):
        self.assertEqual(capture.scale_of(2048, 600), 2.0)

    def test_tall_shot_fits_720(self):
        self.assertEqual(capture.scale_of(1000, 1440), 2.0)

    def test_full_page_caps_width_only(self):
        self.assertEqual(capture.scale_of(1024, 9000, None), 1.0)


class ClipTest(unittest.TestCase):
    def test_short_text_is_kept(self):
        self.assertEqual(reading.clip("abc", "pass a number"), "abc")

    def test_long_text_is_cut_with_a_hint(self):
        clipped = reading.clip("a" * (reading.DEFAULT_CHARS + 5), "pass a number")
        self.assertTrue(clipped.endswith("\n... 5 more chars, pass a number"))
        self.assertEqual(len(clipped.split("\n")[0]), reading.DEFAULT_CHARS)


class RunDirTest(unittest.TestCase):
    def test_git_project_gets_ia_excluded(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            run = target.run_dir(target.git_root(root))
            self.assertEqual(run.parent, root / ".ia" / "browser-bidi")
            self.assertIn(".ia/", (root / ".git" / "info" / "exclude").read_text(encoding="utf-8").split())

    def test_folder_outside_git_goes_to_temp(self):
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(target, "WORK_DIR", Path(folder) / "work"):
            served = Path(folder) / "served"
            served.mkdir()
            with target.Target(str(served)) as page:
                self.assertIsNone(page.root)
                run = target.run_dir(page.root)
            self.assertEqual(run.parent, Path(folder) / "work" / "browser-bidi")
            self.assertEqual(list(served.iterdir()), [])


class UnzipTest(unittest.TestCase):
    def test_driver_is_replaced_without_touching_another_part(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            archive.writestr("chromedriver-win64/chromedriver.exe", b"new")
        with tempfile.TemporaryDirectory() as folder:
            driver = Path(folder) / "chromedriver.exe"
            (Path(folder) / "chromedriver.exe.part").write_bytes(b"other session")
            unzip_to(driver, data.getvalue())
            self.assertEqual(driver.read_bytes(), b"new")
            self.assertEqual(sorted(path.name for path in Path(folder).iterdir()),
                             ["chromedriver.exe", "chromedriver.exe.part"])


if __name__ == "__main__":
    unittest.main()
