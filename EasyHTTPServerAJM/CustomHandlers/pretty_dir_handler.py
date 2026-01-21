from http.server import SimpleHTTPRequestHandler
from html import escape
from pathlib import Path
import os
from string import Template
from socketserver import BaseServer
import socket
from typing import Union, Optional
from EasyHTTPServerAJM.Helpers import AssetHelper


class HTMLTemplateBuilder(AssetHelper):
    def __init__(self, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        super().__init__(html_template_path, **kwargs)
        self.back_svg = Path(self.back_svg_path).read_text(encoding='utf-8')

        # enc = encoding for the HTML page
        self.enc = None
        self.title = None
        self.displaypath = None

    def _build_directory_rows(self, entries, path):
        table_rows = []
        for name in entries:
            table_rows.append(self._process_directory_entry(path, name))
        return table_rows

    def _build_template_safe_context(self, entries, path, add_to_context: dict = None):
        # signature_html = '<br>'.join(self.email_signature.split('\n'))
        parent_dir_link = "<tr><td><a href='..'>..</a></td></tr>" if self.path not in ("/", "") else ""
        rows = '\n'.join(self._build_directory_rows(entries, path))
        full_context = {'title': self.title,
                        'enc': self.enc,
                        'parent_dir_link': parent_dir_link,
                        'rows': rows,
                        'back_svg': self.back_svg}

        return {**full_context, **(add_to_context or {})}

    def _build_body_template(self, context: dict):
        template = Template(Path(self.html_template_path).read_text(encoding='utf-8'))
        return template.safe_substitute(context)

    @staticmethod
    def _process_directory_entry(path, name):
        fullname = os.path.join(path, name)
        # TODO: add stats
        # print(os.stat(fullname))
        display = name + ("/" if os.path.isdir(fullname) else "")
        link = escape(display)
        return f"<tr><td><a href='{link}'>{display}</a></td></tr>"

    def build_page_body(self, entries, path, add_to_context: dict = None) -> str:
        safe_context = self._build_template_safe_context(entries, path, add_to_context)
        return self._build_body_template(safe_context)


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
