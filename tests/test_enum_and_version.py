import unittest
from EasyHTTPServerAJM.Helpers.enum import PathValidationType


class TestEnumIntegrity(unittest.TestCase):
    def test_path_validation_type_members(self):
        names = {m.name for m in PathValidationType}
        values = {m.value for m in PathValidationType}
        self.assertEqual(names, {"DIR", "FILE", "HTML", "SVG", "CSS"})
        self.assertEqual(values, {"dir", "file", "html", "svg", "css"})


if __name__ == "__main__":
    unittest.main()