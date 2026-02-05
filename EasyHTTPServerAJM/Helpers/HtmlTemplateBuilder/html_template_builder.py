import os
from html import escape
from logging import getLogger
from pathlib import Path
from string import Template
from typing import Optional, Union

from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import AssetHelper


class TableWrapperHelper:
    VALID_TABLE_TAGS = ['tr', 'th', 'td']
    TABLE_HEADERS = []

    @classmethod
    def table_header_padding(cls):
        calc_padding = (len(cls.TABLE_HEADERS) - 1)
        return calc_padding if calc_padding >= 0 else 0

    @staticmethod
    def _process_link_entry(link, display_text):
        return f"<a href='{link}'>{display_text}</a>"

    @staticmethod
    def get_table_tag(tag_type, is_end=False):
        if not is_end:
            return f'<{tag_type}>'
        return f'</{tag_type}>'

    def wrap_content_in_tag(self, content, tag):
        if tag in self.__class__.VALID_TABLE_TAGS:
            return f"{self.get_table_tag(tag)}{content}{self.get_table_tag(tag, True)}"
        raise AttributeError(f"tag \'{tag}\' not found in VALID_TABLE_TAGS "
                             f"({self.__class__.VALID_TABLE_TAGS})")

    def wrap_table_row(self, content: str):
        tag = 'tr'
        return self.wrap_content_in_tag(content, tag)

    def wrap_table_data(self, content):
        tag = 'td'
        return self.wrap_content_in_tag(content, tag)

    def wrap_table_header(self, content):
        tag = 'th'
        return self.wrap_content_in_tag(content, tag)


class FormatDirectoryEntryMixin(TableWrapperHelper):
    @staticmethod
    def _get_file_stats(file_path):
        stats = os.stat(file_path)
        from datetime import datetime
        file_stats = {'access_time': datetime.fromtimestamp(stats.st_atime).ctime(),
                      'modified_time': datetime.fromtimestamp(stats.st_mtime).ctime(),
                      'created_time': datetime.fromtimestamp(stats.st_ctime).ctime()}
        return file_stats

    def _format_file_entry_stats(self, file_path):
        fstats = [self.wrap_table_data(f"{x[1]}") for x
                  in self._get_file_stats(file_path=file_path).items()]
        fstats.reverse()
        entry_stats = (''.join(fstats))
        return entry_stats

    def _format_table_data_row(self, entry_stats, **kwargs):
        link, display = kwargs.get('link_tup', (None, None))
        table_data = None

        if link and display:
            table_data = self.wrap_table_data(self._process_link_entry(link, display))

        final_row = [entry_stats, table_data]
        final_row.reverse()

        table_data = (''.join(final_row))
        return table_data

    def _process_directory_entry(self, path, name):
        fullname = os.path.join(path, name)

        display = name + ("/" if os.path.isdir(fullname) else "")
        link = escape(display)

        entry_stats = self._format_file_entry_stats(fullname)
        table_data = self._format_table_data_row(entry_stats, link_tup=(link, display))

        return self.wrap_table_row(table_data)


class HTMLTemplateBuilder(AssetHelper, FormatDirectoryEntryMixin, TableWrapperHelper):
    """
    HTMLTemplateBuilder is a utility class for managing and building HTML templates.

    This class is designed to handle the generation and customization of HTML
    templates with additional features such as incorporating CSS contents, SVG
    backdrops, and dynamic table rows based on directory entries. It is intended
    to simplify the creation of HTML pages for directory listings or related use
    cases by managing templates, context, and injected elements internally.

    Inheritance:
        AssetHelper: Inherits functionality from the AssetHelper base class.

    :ivar back_svg: Stores the SVG contents for the background, if available.
    :ivar dir_page_css: Contains the CSS contents for directory pages, if available.
    :ivar enc: Specifies the character encoding for the HTML page.
    :ivar title: Title of the HTML page.
    :ivar displaypath: Path for display purposes in the HTML page.
    :ivar path: Path to be used for naming and reference within the HTML template.
    """

    TABLE_HEADERS = ['Name', 'access_time', 'modified_time', 'created_time']

    def __init__(self, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        self.logger = kwargs.pop('logger', getLogger(__name__))
        super().__init__(html_template_path, logger=self.logger, **kwargs)
        self.back_svg = None
        self.dir_page_css = None

        self._load_injected_html()

        # enc = encoding for the HTML page
        self.enc = None
        self.title = None
        self.displaypath = None
        self.path = None

    def _load_injected_html(self):
        if self.back_svg_path:
            self.back_svg = self._read_text_file(self.back_svg_path)
        else:
            self.logger.error("back_svg could not be loaded.")

        if self.directory_page_css_path:
            self.dir_page_css = self._read_text_file(self.directory_page_css_path)
        else:
            self.dir_page_css = None
            self.logger.error("directory_page_css could not be loaded.")

    def _read_text_file(self, path: Union[str, Path]):
        try:
            return Path(path).read_text(encoding='utf-8')
        except TypeError as e:
            self.logger.error(f"Could not read file {path}")
            raise FileNotFoundError(f"Could not read file {path}") from e

    def _build_directory_rows(self, entries, path):
        table_rows = []
        for name in entries:
            table_rows.append(self._process_directory_entry(path, name))
        return table_rows

    def _build_parent_dir_link(self):
        # <td><a href='..'>..</a></td>
        pdl_base = self.wrap_table_data(self._process_link_entry('..','..'))
        pdl_with_padding = [pdl_base, (self.wrap_table_data(' ') * self.__class__.table_header_padding())]

        parent_dir_link = self.wrap_table_row(f"{' '.join(pdl_with_padding)}")
        parent_dir_link = parent_dir_link if self.path not in ("/", "") else ""

        return parent_dir_link

    def _build_final_table_headers(self):
        headers = ''.join([self.wrap_table_header(x) for x in self.__class__.TABLE_HEADERS])
        return headers

    def _get_std_table_content(self, entries, path):
        parent_dir_link = self._build_parent_dir_link()
        rows = '\n'.join(self._build_directory_rows(entries, path))
        headers = self._build_final_table_headers()
        return parent_dir_link, headers, rows

    def _build_template_safe_context(self, entries, path, add_to_context: dict = None):
        # signature_html = '<br>'.join(self.email_signature.split('\n'))
        parent_dir_link, headers, rows = self._get_std_table_content(entries, path)

        full_context = {'title': self.title,
                        'table_headers': headers,
                        'enc': self.enc,
                        'parent_dir_link': parent_dir_link,
                        'rows': rows,
                        'back_svg': self.back_svg,
                        'css_contents': self.dir_page_css}

        return {**full_context, **(add_to_context or {})}

    def _build_body_template(self, context: dict):
        try:
            template = Template(self._read_text_file(self.html_template_path))
            return template.safe_substitute(context)
        except FileNotFoundError as e:
            self.logger.critical(f"Could not read template file {self.html_template_path}")
            raise e

    def build_page_body(self, entries, path, add_to_context: dict = None) -> str:
        safe_context = self._build_template_safe_context(entries, path, add_to_context)
        return self._build_body_template(safe_context)
