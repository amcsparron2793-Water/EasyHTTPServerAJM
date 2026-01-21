import os
from html import escape
from logging import getLogger
from pathlib import Path
from string import Template
from typing import Optional, Union

from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import AssetHelper


class HTMLTemplateBuilder(AssetHelper):
    def __init__(self, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        self.logger = kwargs.pop('logger', getLogger(__name__))
        super().__init__(html_template_path, logger=self.logger, **kwargs)
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
