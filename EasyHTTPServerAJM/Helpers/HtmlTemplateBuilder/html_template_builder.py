from html import escape
from logging import getLogger
from pathlib import Path
from string import Template
from typing import Optional, Union

from EasyHTTPServerAJM.Helpers import GetUploadSize
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import (AssetHelper, UploadAssetHelper,
                                                           TableWrapperHelper, HTMLWrapperHelper, FileServerMixin)


class HTMLTemplateBuilder(AssetHelper, TableWrapperHelper):
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

    def _build_template_safe_context(self, entries, path, add_to_context: dict = None):
        full_context = {'title': self.title,
                        'enc': self.enc,
                        'back_svg': self.back_svg,
                        'css_contents': self.dir_page_css}

        return {**full_context, **(add_to_context or {})}

    def _build_template(self, template_path:Path, context: dict):
        try:
            template = Template(self._read_text_file(template_path))
            return template.safe_substitute(context)
        except FileNotFoundError as e:
            self.logger.critical(f"Could not read template file {template_path}")
            raise e

    def _build_body_template(self, context: dict):
        return self._build_template(self.html_template_path, context)

    def build_page_body(self, entries, path, add_to_context: dict = None) -> str:
        safe_context = self._build_template_safe_context(entries, path, add_to_context)
        return self._build_body_template(safe_context)


class FileServerHTMLTemplateBuilder(FileServerMixin, HTMLTemplateBuilder, AssetHelper):
    ...


class FileServerTemplateUpload(FileServerHTMLTemplateBuilder, UploadAssetHelper, HTMLWrapperHelper):
    DEFAULT_UPLOAD_FORM_PATH = Path(HTMLTemplateBuilder.DEFAULT_TEMPLATES_PATH, '_upload_form.html')

    def _get_upload_success_msg(self, filename, data_len: int):
        data_len_str = GetUploadSize.conversion_to_str('auto_convert', data_len)
        return self.wrap_success_paragraph(f'Uploaded {escape(filename)} ({data_len_str})')

    def _get_upload_fail_msg(self, exception):
        msg = self.wrap_error_paragraph(f"Upload failed: {escape(str(exception))}")
        return msg

    # noinspection PyMethodMayBeStatic
    def _build_upload_form(self, context: dict = None):
        if context is None:
            context = {}
        upload_form = self._build_template(self.upload_form_path, context)
        return upload_form

    def _build_template_safe_context(self, entries, path, add_to_context: dict = None):
        context = super()._build_template_safe_context(entries, path, add_to_context)
        context['upload_form'] = self._build_upload_form()
        return context
