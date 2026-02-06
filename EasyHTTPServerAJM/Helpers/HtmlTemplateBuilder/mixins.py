import os
from html import escape
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder import TableWrapperHelper


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
