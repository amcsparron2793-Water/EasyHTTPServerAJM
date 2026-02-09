from http.server import SimpleHTTPRequestHandler
from html import escape
from logging import getLogger
import os
from socketserver import BaseServer
import socket
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import (HTMLTemplateBuilder,
                                                           FileServerHTMLTemplateBuilder,
                                                           FileServerTemplateUpload)
from EasyHTTPServerAJM.CustomHandlers.mixins import UploadHandlerMixin


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
            kwargs.pop('html_template_builder_class', FileServerHTMLTemplateBuilder)(
                self.html_template_path, logger=self.logger, **kwargs
            )
        )
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

    def _get_directory_entries(self, path):
        try:
            entries = sorted(os.listdir(path))
            self.logger.debug(f"Listing directory {path}")
            return entries
        except OSError:
            self.logger.warning(f"Failed to list directory {path}")
            self.send_error(404, "No permission to list directory")
            return None

    def _render_directory(self, path, add_to_context: dict = None):
        entries = self._get_directory_entries(path)
        if not entries:
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


class UploadPrettyDirectoryHandler(PrettyDirectoryHandler, UploadHandlerMixin):
    def __init__(self, request: socket.SocketType, client_address, server: BaseServer, **kwargs):
        kwargs['html_template_builder_class'] = FileServerTemplateUpload
        super().__init__(request, client_address, server, **kwargs)

    # noinspection PyProtectedMember,PyUnresolvedReferences
    def _get_upload_success_msg(self, filename, data_len: int):
        return self.template_builder._get_upload_success_msg(filename, data_len)

    # noinspection PyProtectedMember,PyUnresolvedReferences
    def _get_upload_fail_msg(self, exception):
        return self.template_builder._get_upload_fail_msg(exception)
