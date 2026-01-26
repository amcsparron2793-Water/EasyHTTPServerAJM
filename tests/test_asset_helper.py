import unittest
from pathlib import Path

from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import AssetHelper


def project_root() -> Path:
    # tests directory is under project root
    real_project_root = Path(__file__).resolve().parent.parent
    template_root = Path("EasyHTTPServerAJM", 'Helpers', 'HtmlTemplateBuilder')
    test_project_root = Path(real_project_root, template_root)
    return test_project_root


class TestAssetHelper(unittest.TestCase):
    def setUp(self):
        self.assets = project_root() / "assets"
        self.templates = project_root() / "templates"
        self.svg = self.assets / "BackBoxWithText.svg"
        self.css = self.templates / "directory_page.css"
        self.html = self.templates / "directory_page_template.html"
        # sanity that repo files exist
        for p in (self.assets, self.templates, self.svg, self.css, self.html):
            self.assertTrue(p.exists(), f"Expected path to exist in repo: {p}")

    def test_override_paths_are_set_and_valid(self):
        ah = AssetHelper(
            html_template_path=self.html,
            templates_path=self.templates,
            assets_path=self.assets,
            back_svg_path=self.svg,
            directory_page_css_path=self.css,
        )
        self.assertEqual(Path(ah.html_template_path), self.html)
        self.assertEqual(Path(ah.templates_path), self.templates)
        self.assertEqual(Path(ah.assets_path), self.assets)
        self.assertEqual(Path(ah.back_svg_path), self.svg)
        self.assertEqual(Path(ah.directory_page_css_path), self.css)

    def test_invalid_css_fails_validation_leaves_attr_none(self):
        invalid_css = self.templates / "missing.css"
        self.assertFalse(invalid_css.exists())
        ah = AssetHelper(
            html_template_path=self.html,
            templates_path=self.templates,
            assets_path=self.assets,
            back_svg_path=self.svg,
            directory_page_css_path=invalid_css,
        )
        # valid ones set
        self.assertEqual(Path(ah.html_template_path), self.html)
        self.assertEqual(Path(ah.back_svg_path), self.svg)
        # invalid CSS path should not be set (remains None)
        self.assertIsNone(ah.directory_page_css_path)


if __name__ == "__main__":
    unittest.main()
