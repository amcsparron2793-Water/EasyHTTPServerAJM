import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from EasyHTTPServerAJM.Helpers.path_validator import PathValidator, CandidatePathNotSetError
from EasyHTTPServerAJM.Helpers.enum import PathValidationType


class TestPathValidator(unittest.TestCase):
    def test_error_when_candidate_not_set(self):
        pv = PathValidator()
        with self.assertRaises(CandidatePathNotSetError):
            pv.resolve_flags()

    def test_resolve_dir_and_file_flags(self):
        with TemporaryDirectory() as td:
            tmpdir = Path(td)
            # Create files
            html_f = tmpdir / "index.html"
            css_f = tmpdir / "style.css"
            svg_f = tmpdir / "icon.svg"
            txt_f = tmpdir / "readme.txt"
            for p in (html_f, css_f, svg_f, txt_f):
                p.write_text("data", encoding="utf-8")

            cases = [
                (tmpdir, PathValidationType.DIR, True),
                (html_f, PathValidationType.HTML, True),
                (css_f, PathValidationType.CSS, True),
                (svg_f, PathValidationType.SVG, True),
                (txt_f, PathValidationType.FILE, True),
            ]

            for cand, vt, expected in cases:
                with self.subTest(cand=cand, vt=vt):
                    pv = PathValidator(candidate_path=cand, candidate_path_validation_type=vt)
                    pv.resolve_flags()
                    self.assertEqual(pv.validate(), expected)

    def test_nonexistent_path_is_invalid(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path as _P
        with TemporaryDirectory() as td:
            missing = _P(td) / "nope" / "missing.txt"
            pv = PathValidator(candidate_path=missing, candidate_path_validation_type=PathValidationType.FILE)
            pv.resolve_flags()
            self.assertFalse(pv.validate())

    def test_dynamic_attribute_access(self):
        with TemporaryDirectory() as td:
            html_f = Path(td) / "index.HTML"  # ensure case-insensitive suffix handling via lower()
            html_f.write_text("<html></html>", encoding="utf-8")
            pv = PathValidator(candidate_path=html_f, candidate_path_validation_type=PathValidationType.HTML)
            pv.resolve_flags()
            # dynamic flags should be exposed
            self.assertTrue(pv.is_resolved_to_html)
            self.assertFalse(pv.is_resolved_to_css)
            self.assertFalse(pv.is_resolved_to_svg)


if __name__ == "__main__":
    unittest.main()
