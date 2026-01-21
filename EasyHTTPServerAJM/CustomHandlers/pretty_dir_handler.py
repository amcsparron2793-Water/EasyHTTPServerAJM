from http.server import SimpleHTTPRequestHandler
from html import escape
from logging import getLogger
import os
from socketserver import BaseServer
import socket
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import HTMLTemplateBuilder


class PrettyDirectoryHandler(SimpleHTTPRequestHandler):
    def __init__(self, request: socket.SocketType, client_address,
                 server: BaseServer, **kwargs):
        self.logger = kwargs.pop('logger', getLogger(__name__))
        self.html_template_path = kwargs.pop('html_template_path', None)
        self.template_builder = HTMLTemplateBuilder(self.html_template_path, logger=self.logger)
        self.template_builder.enc = "utf-8"

        super().__init__(request, client_address, server)

    def _setup_template_builder_for_page(self):
        self.template_builder.displaypath = escape(self.path)
        self.template_builder.path = self.path
        self.template_builder.title = f"Index of {self.template_builder.displaypath}"
        self.logger.debug(f"Setting up template builder for page {self.template_builder.displaypath}")

    def _send_response_code_and_headers(self, encoded):
        self.send_response(200)
        self.send_header("Content-type", f"text/html; charset={self.template_builder.enc}")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.logger.debug(f"Sent headers for {self.template_builder.displaypath}")

    def list_directory(self, path):
        """Generate a custom HTML directory listing."""
        # path = path to the directory you want listed
        try:
            entries = sorted(os.listdir(path))
            self.logger.debug(f"Listing directory {path}")
        except OSError:
            self.logger.warning(f"Failed to list directory {path}")
            self.send_error(404, "No permission to list directory")
            return None

        self._setup_template_builder_for_page()

        page_body = self.template_builder.build_page_body(entries, path)
        encoded = page_body.encode(self.template_builder.enc, "surrogateescape")

        # Send HTTP headers
        self._send_response_code_and_headers(encoded)

        self.wfile.write(encoded)
        self.logger.info(f"Sent directory listing for {self.template_builder.displaypath}")
        return None
