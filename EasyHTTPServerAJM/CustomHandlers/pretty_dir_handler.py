from http.server import SimpleHTTPRequestHandler
from html import escape
from pathlib import Path
import os
from string import Template
from socketserver import BaseServer
import socket
from typing import Union, Optional


class _AssetHelper:
    ...


class HTMLTemplateBuilder:
    DEFAULT_ASSETS_PATH = Path('../Misc_Project_Files/assets').resolve()
    DEFAULT_TEMPLATES_PATH = Path('../Misc_Project_Files/templates').resolve()
    DEFAULT_HTML_TEMPLATE_PATH = Path(DEFAULT_TEMPLATES_PATH, 'directory_page_template.html').resolve()
    DEFAULT_BACK_SVG_PATH = Path(DEFAULT_ASSETS_PATH, 'back.svg').resolve()

    def __init__(self, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        self._templates_path = None
        self._html_template_path = None
        self._assets_path = None
        self._back_svg_path = None

        self.html_template_path = (html_template_path if html_template_path is not None
                                   else self.__class__.DEFAULT_HTML_TEMPLATE_PATH)
        self.assets_path = kwargs.get('assets_path', self.__class__.DEFAULT_ASSETS_PATH)
        self.back_svg_path = kwargs.get('back_svg_path', self.__class__.DEFAULT_BACK_SVG_PATH)
        self.back_svg = Path(self.back_svg_path).read_text(encoding='utf-8')

        # enc = encoding for the HTML page
        self.enc = None
        self.title = None
        self.displaypath = None

    @staticmethod
    def _resolve_path(candidate_path: Union[str, Path]) -> Path:
        if isinstance(candidate_path, str):
            candidate_path = Path(candidate_path).resolve()
        elif isinstance(candidate_path, Path):
            candidate_path = candidate_path.resolve()
        else:
            raise ValueError(f"{candidate_path} is not a valid path")
        return candidate_path

    def _is_resolved_to_dir(self, candidate_path: Union[str, Path]) -> bool:
        candidate_path = self._resolve_path(candidate_path)
        if candidate_path.is_dir():
            return True
        else:
            raise ValueError(f"{candidate_path} is not a valid directory")

    def _is_resolved_to_html(self, candidate_path: Union[str, Path]) -> bool:
        candidate_path = self._resolve_path(candidate_path)
        if candidate_path.is_file() and candidate_path.suffix == '.html':
            return True
        else:
            raise ValueError(f"{candidate_path} is not a valid html file")

    def _is_resolved_to_svg(self, candidate_path: Union[str, Path]) -> bool:
        candidate_path = self._resolve_path(candidate_path)
        if candidate_path.is_file() and candidate_path.suffix == '.svg':
            return True
        else:
            raise ValueError(f"{candidate_path} is not a valid svg file")

    @property
    def templates_path(self):
        return self._templates_path

    @templates_path.setter
    def templates_path(self, value: Union[str, Path]):
        if self._is_resolved_to_dir(value):
            self._templates_path = self._resolve_path(value)

    @property
    def html_template_path(self):
        return self._html_template_path

    @html_template_path.setter
    def html_template_path(self, value: Union[str, Path]):
        if self._is_resolved_to_html(value):
            self._html_template_path = self._resolve_path(value)

    @property
    def assets_path(self):
        return self._assets_path

    @assets_path.setter
    def assets_path(self, value: Union[str, Path]):
        if self._is_resolved_to_dir(value):
            self._assets_path = self._resolve_path(value)

    @property
    def back_svg_path(self):
        return self._back_svg_path

    @back_svg_path.setter
    def back_svg_path(self, value: Union[str, Path]):
        if self._is_resolved_to_svg(value):
            self._back_svg_path = self._resolve_path(value)

    def _build_directory_rows(self, entries, path):
        table_rows = []
        for name in entries:
            table_rows.append(self._process_directory_entry(path, name))
        return table_rows

    def _build_template_safe_context(self, entries, path, add_to_context: dict = None):

        # signature_html = '<br>'.join(self.email_signature.split('\n'))
        parent_dir_link = "<tr><td><a href='..'>..</a></td></tr>" if self.path not in ("/", "") else ""
        rows = '\n'.join(self._build_directory_rows(entries, path))
        # full_context = {'fast_update_html': fast_update_html,
        #                 'manager_contact_html': manager_contact_html,
        #                 'signature_html': signature_html,
        #                 'tab_char': self.tab_char}
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
