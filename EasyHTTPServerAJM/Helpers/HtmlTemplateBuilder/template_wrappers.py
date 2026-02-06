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

    # TODO: add to TableWrapperHelper
    @staticmethod
    def get_table_tag(tag_type, is_end=False, **kwargs):
        style = kwargs.get('style', None)
        if not is_end:
            if not style:
                return f'<{tag_type}>'
            else:
                return f"<{tag_type} style='{style}'>"
        return f'</{tag_type}>'

    def wrap_content_in_tag(self, content, tag, **kwargs):
        if tag in self.__class__.VALID_TABLE_TAGS:
            return f"{self.get_table_tag(tag, **kwargs)}{content}{self.get_table_tag(tag, True, **kwargs)}"
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


class HTMLWrapperHelper(TableWrapperHelper):
    VALID_TABLE_TAGS = TableWrapperHelper.VALID_TABLE_TAGS + ['p']

    def wrap_error_paragraph(self, content):
        tag = 'p'
        style = 'color:red;'
        return self.wrap_content_in_tag(content, tag, style=style)

    def wrap_success_paragraph(self, content):
        tag = 'p'
        style = 'color:green;'
        return self.wrap_content_in_tag(content, tag, style=style)
