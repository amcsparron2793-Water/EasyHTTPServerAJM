from typing import Union, Optional

from EasyHTTPServerAJM._version import __version__
from EasyHTTPServerAJM.CustomHandlers import PrettyDirectoryHandler
import argparse
from http.server import ThreadingHTTPServer
from socketserver import TCPServer
from os import chdir
from pathlib import Path


# TODO: needs logging support
class EasyHTTPServer:
    """
    Basic class-based HTTP server for file sharing.

    - Serves files from a given directory (default: current directory).
    - Uses Python's built-in http.server.SimpleHTTPRequestHandler.
    - Intended for quick, local file sharing on trusted networks.
    """

    DEFAULT_HANDLER_CLASS = PrettyDirectoryHandler#SimpleHTTPRequestHandler
    DEFAULT_PORT = 8000
    DEFAULT_DIRECTORY = "."
    DEFAULT_HOST = "0.0.0.0"

    def __init__(self, directory: Optional[Union[Path, str]] = None,
                 host: Optional[str] = None, port: Optional[int] = None, **kwargs) -> None:

        self.directory = Path(directory) if directory is not None else Path(self.__class__.DEFAULT_DIRECTORY)
        self.host = host if host is not None else self.__class__.DEFAULT_HOST
        self.port = int(port) if port is not None else self.__class__.DEFAULT_PORT

        self.handler_class = kwargs.get("handler_class", self.__class__.DEFAULT_HANDLER_CLASS)

        if not self.directory.exists() or not self.directory.is_dir():
            raise ValueError(f"{self.directory} is not a valid directory")

        self._httpd: Optional[TCPServer] = None

    @classmethod
    def from_cli(cls) -> "EasyHTTPServer":
        """Create an EasyHTTPServer instance using command-line arguments."""
        args = cls._parse_args()
        return cls(directory=args.directory, host=args.host, port=args.port)

    @staticmethod
    def _parse_args() -> argparse.Namespace:
        """Parse command-line arguments for the HTTP server."""
        parser = argparse.ArgumentParser(description="Simple HTTP file-sharing server.")
        parser.add_argument(
            "-d",
            "--directory",
            default=".",
            help="Directory to share (default: current directory)",
        )
        parser.add_argument(
            "-H",
            "--host",
            default="0.0.0.0",
            help="Host/IP to bind to (default: 0.0.0.0 = all interfaces)",
        )
        parser.add_argument(
            "-p",
            "--port",
            type=int,
            default=8000,
            help="Port to listen on (default: 8000)",
        )
        return parser.parse_args()

    def start(self) -> None:
        """Start the HTTP server and block until interrupted (Ctrl+C)."""
        chdir(self.directory)

        with ThreadingHTTPServer((self.host, self.port), self.handler_class) as httpd:
            self._httpd = httpd
            print(f"EasyHTTPServerAJM v{__version__}")
            # noinspection HttpUrlsUsage
            print(f"Serving directory {self.directory.resolve()} at http://{self.host}:{self.port}")
            print("Press Ctrl+C to stop.")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")

    def stop(self) -> None:
        """
        Stop the server if it's running.
        (Only useful if you manage the server in a separate thread/process.)
        """
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None


if __name__ == "__main__":
    # TODO: make both CLI and class-based usage possible
    srv = EasyHTTPServer()
    srv.start()
