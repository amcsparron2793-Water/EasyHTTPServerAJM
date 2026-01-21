from http.server import SimpleHTTPRequestHandler
from html import escape
from logging import getLogger
from pathlib import Path
import os
from socketserver import BaseServer
import socket
from typing import Union, Optional
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import HTMLTemplateBuilder


class PrettyDirectoryHandler(SimpleHTTPRequestHandler, HTMLTemplateBuilder):
    def __init__(self, request: socket.SocketType, client_address,
                 server: BaseServer, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        self.logger = kwargs.pop('logger', getLogger(__name__))
        # TODO: dont make this inherit the TemplateBuilder class, just make it an attr
        HTMLTemplateBuilder.__init__(self, html_template_path, logger=self.logger)
        super().__init__(request, client_address, server)

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

        self.displaypath = escape(self.path)
        self.enc = "utf-8"
        self.title = f"Index of {self.displaypath}"

        page_body = self.build_page_body(entries, path)
        encoded = page_body.encode(self.enc, "surrogateescape")

        # Send HTTP headers
        self.send_response(200)
        self.send_header("Content-type", f"text/html; charset={self.enc}")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        self.logger.debug(f"Sent directory listing for {self.displaypath}")
        return None
