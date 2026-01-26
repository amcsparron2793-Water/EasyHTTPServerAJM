import unittest
from pathlib import Path

from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import HTMLTemplateBuilder


def project_root() -> Path:
    # tests directory is under project root
    real_project_root = Path(__file__).resolve().parent.parent
    template_root = Path("EasyHTTPServerAJM", 'Helpers', 'HtmlTemplateBuilder')
    test_project_root = Path(real_project_root, template_root)
    return test_project_root


class TestHTMLTemplateBuilder(unittest.TestCase):
    def setUp(self):
        self.assets = project_root() / "assets"
        self.templates = project_root() / "templates"
        self.svg = self.assets / "BackBoxWithText.svg"
        self.css = self.templates / "directory_page.css"
        self.html = self.templates / "directory_page_template.html"
        for p in (self.assets, self.templates, self.svg, self.css, self.html):
            self.assertTrue(p.exists(), f"Expected path to exist in repo: {p}")

    def _builder(self) -> HTMLTemplateBuilder:
        return HTMLTemplateBuilder(
            html_template_path=self.html,
            templates_path=self.templates,
            assets_path=self.assets,
            back_svg_path=self.svg,
            directory_page_css_path=self.css,
        )

    def test_injected_assets_are_loaded(self):
        b = self._builder()
        self.assertIsInstance(b.back_svg, str)
        self.assertGreater(len(b.back_svg), 0)
        self.assertIsInstance(b.dir_page_css, str)
        self.assertGreater(len(b.dir_page_css), 0)

    def test_build_page_body_root_path_hides_parent_link(self):
        # Create a deterministic directory structure for the builder to inspect
        from tempfile import TemporaryDirectory
        from pathlib import Path as _P
        with TemporaryDirectory() as td:
            tdp = _P(td)
            (tdp / "a.txt").write_text("hi", encoding="utf-8")
            (tdp / "folder").mkdir()

            b = self._builder()
            b.enc = "utf-8"
            b.title = "Index of /"
            b.path = "/"  # root -> no parent link
            entries = sorted([p.name for p in tdp.iterdir()])
            page = b.build_page_body(entries, path=str(tdp))
            # No parent link row, but entries rendered with folder suffix
            self.assertNotIn("<a href='..'>..</a>", page)
            self.assertIn("<a href='a.txt'>a.txt</a>", page)
            self.assertIn("<a href='folder/'>folder/</a>", page)
            # Title substituted
            self.assertIn("<title>Index of /</title>", page)
            # CSS and SVG injected
            self.assertIn("<style>", page)
            self.assertIn("</style>", page)
            self.assertIn("svg", page)

    def test_build_page_body_subpath_shows_parent_link(self):
        b = self._builder()
        b.enc = "utf-8"
        b.title = "Index of /sub"
        b.path = "/sub"  # not root -> show parent link
        page = b.build_page_body(["x"], path=str(project_root()))
        self.assertIn("<a href='..'>..</a>", page)


if __name__ == "__main__":
    unittest.main()
