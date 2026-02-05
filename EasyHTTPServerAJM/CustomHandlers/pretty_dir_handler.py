from http.server import SimpleHTTPRequestHandler
from html import escape
from logging import getLogger
import os
from socketserver import BaseServer
import socket
import cgi
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import HTMLTemplateBuilder


class PrettyDirectoryHandler(SimpleHTTPRequestHandler):
    """
    Handles HTTP requests to provide custom directory listings in a user-friendly HTML format.

    This handler overrides the default `SimpleHTTPRequestHandler` to generate a dynamic,
    template-based directory listing with enhanced customization. It enables integration
    of custom HTML templates and logging functionalities.

    :ivar logger: Logger instance for logging debug and informational messages.
    :type logger: logging.Logger
    :ivar html_template_path: Path to the HTML template used for rendering the directory.
    :type html_template_path: str or None
    :ivar template_builder: Instance of the HTML template builder responsible for creating
        directory page content.
    :type template_builder: HTMLTemplateBuilder
    """
    def __init__(self, request: socket.SocketType, client_address,
                 server: BaseServer, **kwargs):
        self.logger = kwargs.pop('logger', getLogger(__name__))
        self.html_template_path = kwargs.pop('html_template_path', None)
        self.template_builder = (
            kwargs.pop('html_template_builder_class', HTMLTemplateBuilder)(
                self.html_template_path, logger=self.logger, **kwargs
            )
        )
        self.template_builder.enc = "utf-8"

        super().__init__(request, client_address, server)

    @staticmethod
    def _safe_filename(name: str) -> str:
        base = os.path.basename(name)
        # Replace path separators and risky characters
        safe = ''.join(c for c in base if c.isalnum() or c in (' ', '.', '-', '_'))
        return safe or 'upload.bin'

    def _unique_path(self, directory: str, filename: str) -> str:
        candidate = os.path.join(directory, filename)
        if not os.path.exists(candidate):
            return candidate
        root, ext = os.path.splitext(filename)
        i = 1
        while True:
            new_name = f"{root} ({i}){ext}"
            candidate = os.path.join(directory, new_name)
            if not os.path.exists(candidate):
                return candidate
            i += 1

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('Content-Type', ''))
        if ctype != 'multipart/form-data':
            self.send_error(400, "Unsupported Content-Type")
            return
        pdict['boundary'] = pdict['boundary'].encode() if isinstance(pdict.get('boundary'), str) else pdict.get('boundary')
        # Use FieldStorage to parse the incoming data stream
        try:
            form = cgi.FieldStorage(fp=self.rfile,
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST',
                                             'CONTENT_TYPE': self.headers.get('Content-Type')})
        except Exception as e:
            self.logger.exception("Failed to parse multipart form data")
            return self._render_directory(self.translate_path(self.path),
                                          { 'message': f"<p style='color:red;'>Upload failed: {escape(str(e))}</p>" })

        field = form.getvalue('file', None)
        if not getattr(field, 'filename', None):
            return self._render_directory(self.translate_path(self.path),
                                          { 'message': "<p style='color:red;'>No file provided.</p>" })

        directory = self.translate_path(self.path)
        if not os.path.isdir(directory):
            self.send_error(400, "Upload path is not a directory")
            return

        filename = self._safe_filename(field.filename)
        dest_path = self._unique_path(directory, filename)
        try:
            with open(dest_path, 'wb') as out:
                data = field.file.read()
                out.write(data)
            msg = f"<p style='color:green;'>Uploaded {escape(filename)} ({len(data)} bytes)</p>"
            self.logger.info(f"Uploaded file saved to {dest_path}")
        except Exception as e:
            self.logger.exception("Error saving uploaded file")
            msg = f"<p style='color:red;'>Failed to save file: {escape(str(e))}</p>"

        return self._render_directory(directory, { 'message': msg })

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

    def _render_directory(self, path, add_to_context: dict = None):
        try:
            entries = sorted(os.listdir(path))
            self.logger.debug(f"Listing directory {path}")
        except OSError:
            self.logger.warning(f"Failed to list directory {path}")
            self.send_error(404, "No permission to list directory")
            return None

        self._setup_template_builder_for_page()

        page_body = self.template_builder.build_page_body(entries, path, add_to_context)
        encoded = page_body.encode(self.template_builder.enc, "surrogateescape")

        # Send HTTP headers
        self._send_response_code_and_headers(encoded)

        self.wfile.write(encoded)
        self.logger.info(f"Sent directory listing for {self.template_builder.displaypath}")
        return None

    def list_directory(self, path):
        """Generate a custom HTML directory listing."""
        return self._render_directory(path)
