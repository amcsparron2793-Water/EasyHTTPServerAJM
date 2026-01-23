import unittest

from EasyHTTPServerAJM.easy_http_server import EasyHTTPServer
from EasyHTTPServerAJM._version import __version__


class TestServerUtils(unittest.TestCase):
    def test_version_and_welcome_string(self):
        # Ensure version is a non-empty string
        self.assertIsInstance(__version__, str)
        self.assertGreater(len(__version__), 0)

        welcome = EasyHTTPServer.get_welcome_string()
        self.assertIn("EasyHTTPServer", welcome)
        self.assertIn(__version__, welcome)


if __name__ == "__main__":
    unittest.main()
