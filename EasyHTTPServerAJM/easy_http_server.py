from datetime import datetime, timedelta
from typing import Union, Optional

from EasyHTTPServerAJM._version import __version__
from EasyHTTPServerAJM.CustomHandlers import PrettyDirectoryHandler
import argparse
from http.server import ThreadingHTTPServer
from socketserver import TCPServer
from os import chdir
from pathlib import Path
from EasyHTTPServerAJM import EasyHTTPLogger


class EasyHTTPServer:
    """
    A simple HTTP server for serving files with directory listing functionality.

    The EasyHTTPServer class provides a lightweight and configurable HTTP server
    for file-sharing purposes. It supports directory browsing, customizable
    handlers, and file-serving options. The server is designed to be started using
    command-line arguments or programmatically.

    :ivar logger: Logger instance to track server events and errors.
    :type logger: EasyHTTPLogger.logger
    :ivar html_template_path: Path to an optional HTML template for custom directory
        listing pages. Defaults to None if not provided.
    :type html_template_path: str, optional
    :ivar directory: Path of the directory to serve. Defaults to the current
        directory if not passed.
    :type directory: Path
    :ivar host: Host/IP address to bind the server to. Defaults to "0.0.0.0",
        which binds to all network interfaces.
    :type host: str
    :ivar port: Port number to run the server. Defaults to 8000.
    :type port: int
    :ivar handler_class: Request handler class to use for managing HTTP requests.
        Can be customized; otherwise, defaults to PrettyDirectoryHandler.
    :type handler_class: type
    :ivar start_time: Timestamp indicating when the server started. None if the
        server has not started yet.
    :type start_time: datetime, optional
    """

    DEFAULT_HANDLER_CLASS = PrettyDirectoryHandler#SimpleHTTPRequestHandler
    DEFAULT_PORT = 8000
    DEFAULT_DIRECTORY = "."
    DEFAULT_HOST = "0.0.0.0"

    def __init__(self, directory: Optional[Union[Path, str]] = None,
                 host: Optional[str] = None, port: Optional[int] = None, **kwargs) -> None:
        self._runtime = None
        self.logger = kwargs.get("logger", EasyHTTPLogger(**kwargs)())
        self.html_template_path = kwargs.get("html_template_path", None)

        self.directory = Path(directory) if directory is not None else Path(self.__class__.DEFAULT_DIRECTORY)
        self.host = host if host is not None else self.__class__.DEFAULT_HOST
        self.port = int(port) if port is not None else self.__class__.DEFAULT_PORT

        self.handler_class = kwargs.get("handler_class", self.__class__.DEFAULT_HANDLER_CLASS)

        if not self.directory.exists() or not self.directory.is_dir():
            raise ValueError(f"{self.directory} is not a valid directory")

        self._httpd: Optional[TCPServer] = None
        self.start_time: Optional[datetime] = None

    @classmethod
    def __version__(cls):
        try:
            return str(__version__)
        except NameError:
            return ' unknown'

    @classmethod
    def from_cli(cls) -> "EasyHTTPServer":
        """Create an EasyHTTPServer instance using command-line arguments."""
        args = cls._parse_args()
        return cls(directory=args.directory, host=args.host, port=args.port)

    @classmethod
    def get_welcome_string(cls) -> str:
        return f"{cls.__name__} v{cls.__version__()}"

    @property
    def serving_info_string(self) -> str:
        # noinspection HttpUrlsUsage
        return f"Serving directory {self.directory.resolve()} at http://{self.host}:{self.port}"

    def _log_all_basic_server_info(self, **kwargs):
        print_msg = kwargs.pop("print_msg", True)
        # noinspection PyArgumentList
        self.logger.info(self.__class__.get_welcome_string(), print_msg=print_msg, **kwargs)
        # noinspection HttpUrlsUsage
        # noinspection PyArgumentList
        self.logger.info(self.serving_info_string, print_msg=print_msg, **kwargs)
        if print_msg:
            print("Press Ctrl+C to stop.")

    @staticmethod
    def _round_timedelta(td: timedelta) -> timedelta:
        return timedelta(seconds=round(td.total_seconds()))

    @property
    def runtime(self):
        if self.start_time:
            raw_run_time = (datetime.now() - self.start_time)
            self._runtime = self._round_timedelta(raw_run_time)
        else:
            self._runtime = 0
        return self._runtime

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

    def _handler_factory(self, request, client_address, server):
        """
        Creates an instance of the specified handler class with the provided parameters.

        This method initializes and returns a handler object using
        the `handler_class` attribute. It passes the necessary arguments
        such as request, client address, server, and additional
        parameters like directory, logger, and HTML template path
        to the handler's constructor.

        :param request: The incoming client request to be handled.
        :param client_address: The address of the client sending the request.
        :param server: The server instance managing the request.
        :return: An instance of the handler class initialized with the given parameters.
        :rtype: handler_class
        """
        try:
            return self.handler_class(request,
                                      client_address,
                                      server,
                                      directory=self.directory,
                                      logger=self.logger,
                                      html_template_path=self.html_template_path)
        except Exception as e:
            self.logger.critical(f"Failed to create handler: {e}")
            self.err_stop()

    def _set_start_time(self):
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        self.start_time = datetime.now().strftime(dt_fmt)
        self.start_time = datetime.strptime(self.start_time, dt_fmt)

    def start(self, **kwargs) -> None:
        """Start the HTTP server and block until interrupted (Ctrl+C)."""
        chdir(self.directory)
        self.logger.debug(f"Changing working directory to {self.directory}")

        # noinspection PyTypeChecker
        with ThreadingHTTPServer((self.host, self.port), self._handler_factory) as httpd:
            # self._httpd seems to only be used by the close method
            self._httpd = httpd

            self._log_all_basic_server_info(**kwargs)

            try:
                self._set_start_time()
                self.logger.info(f"Server started at {self.start_time}", print_msg=True)
                httpd.serve_forever()
            except KeyboardInterrupt:
                self.logger.warning(f"Shutting down server (ran for {self.runtime}).")

    def stop(self) -> None:
        """
        Stop the server if it's running.
        (Only useful if you manage the server in a separate thread/process.)
        """
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None

    def err_stop(self) -> None:
        """
        Stop the server if it's running.
        (Only useful if you manage the server in a separate thread/process.)
        """
        self.stop()
        # FIXME: this error exit seems to be ignored - create my own ThreadingHTTPServer class and override shutdown?
        exit(1)


if __name__ == "__main__":
    srv = EasyHTTPServer()
    srv.start()
