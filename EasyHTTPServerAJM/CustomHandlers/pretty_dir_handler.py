from http.server import SimpleHTTPRequestHandler
from html import escape
from pathlib import Path
import os
from socketserver import BaseServer
import socket
from typing import Union, Optional
from EasyHTTPServerAJM.Helpers import HTMLTemplateBuilder


class PrettyDirectoryHandler(SimpleHTTPRequestHandler, HTMLTemplateBuilder):
    def __init__(self, request: socket.SocketType, client_address,
                 server: BaseServer, html_template_path: Optional[Union[str, Path]] = None):
        HTMLTemplateBuilder.__init__(self, html_template_path)
        super().__init__(request, client_address, server)

    def list_directory(self, path):
        """Generate a custom HTML directory listing."""
        # path = path to the directory you want listed
        try:
            entries = sorted(os.listdir(path))
        except OSError:
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
        return None
