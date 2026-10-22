import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))

from choices import EMPTY, NOTE_LIMIT, describe, normalize, summary
from gitrepo import has_exclude
from page import is_full, render
from session import inside_root, slug
from spec import content_problems, empty_sections, name_problems, placeholders

GOOD_SPEC = Path("C:/work/shop/.ia/specs/2026-10-22-book-loans-design.md")


class SpecNameTest(unittest.TestCase):
    def test_good_path(self):
        self.assertEqual(name_problems(GOOD_SPEC), [])

    def test_wrong_name(self):
        problems = name_problems(GOOD_SPEC.with_name("loans.md"))
        self.assertEqual(len(problems), 1)
        self.assertIn("does not follow", problems[0])

    def test_wrong_folder(self):
        problems = name_problems(Path("C:/work/shop/docs/specs/2026-10-22-book-loans-design.md"))
        self.assertEqual(len(problems), 1)
        self.assertIn("is not in", problems[0])


class SpecContentTest(unittest.TestCase):
    def test_placeholders(self):
        lines = ["# Prets", "Le rappel part apres TODO jours.", "Une todo-list simple.", "Delai a definir.",
                 "Tarif à préciser plus tard.", "Rien à voir avec le panier."]
        self.assertEqual(placeholders(lines), [2, 4, 5])

    def test_placeholders_inside_code_are_left(self):
        self.assertEqual(placeholders(["# Code", "```python", "# TODO later", "```"]), [])

    def test_empty_sections(self):
        lines = ["# Prets", "", "## But", "", "## Donnees", "Un fichier.", "## Tests"]
        self.assertEqual(empty_sections(lines), [3, 7])

    def test_parent_with_subsections_is_not_empty(self):
        self.assertEqual(empty_sections(["# Prets", "## But", "Savoir qui a quoi."]), [])

    def test_section_holding_only_code(self):
        self.assertEqual(empty_sections(["# Prets", "## Format", "```json", "{}", "```", "## Fin", "ok"]), [])

    def test_no_heading(self):
        self.assertIn("no heading", content_problems(["juste du texte"])[0])


class ExcludeTest(unittest.TestCase):
    def test_forms(self):
        for text in (".ia/\n", "# local\n/.ia\n", "node_modules/\n.ia\n"):
            self.assertTrue(has_exclude(text), text)
        self.assertFalse(has_exclude(".idea/\n# .ia/ later\n"))


class ChoiceTest(unittest.TestCase):
    def test_normalize(self):
        screen, entry = normalize({"screen": "layout.html", "selected": {"mise": ["b", 2]}, "note": "x" * 5000,
                                   "sent": 1})
        self.assertEqual(screen, "layout.html")
        self.assertEqual(entry["selected"], {"mise": ["b", "2"]})
        self.assertEqual(len(entry["note"]), NOTE_LIMIT)
        self.assertTrue(entry["sent"])

    def test_refusals(self):
        for payload in ([], {"selected": {}}, {"screen": "a.html", "selected": ["b"]}):
            with self.assertRaises(ValueError):
                normalize(payload)

    def test_describe(self):
        entry = {"selected": {"mise": ["b"], "couleur": []}, "note": " plus clair ", "sent": False}
        self.assertEqual(describe("layout.html", entry),
                         "layout.html: ticked, not sent yet, mise = b; couleur = nothing, note: plus clair")
        self.assertEqual(summary({}), [EMPTY])


class PageTest(unittest.TestCase):
    def test_full_document(self):
        self.assertTrue(is_full("\n  <!DOCTYPE html><html></html>"))
        self.assertFalse(is_full("<h1>Choix</h1>"))

    def test_render_escapes_the_name_only(self):
        frame = "<b>{{screen}}</b><i>{{version}}</i>{{content}}"
        self.assertEqual(render(frame, "a<b>.html", "<p>{{screen}}</p>", "v1"),
                         "<b>a&lt;b&gt;.html</b><i>v1</i><p>{{screen}}</p>")


class SessionTest(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(slug("Fiche Produit, version 2!"), "fiche-produit-version-2")
        self.assertEqual(slug("!!!"), "session")

    def test_inside_root(self):
        root = Path("C:/temp/claude-skills/concevoir")
        self.assertTrue(inside_root(root / "fiche-20261022-101500", root))
        self.assertFalse(inside_root(root, root))
        self.assertFalse(inside_root(root / "a" / "b", root))


if __name__ == "__main__":
    unittest.main()
