import cgi
import os
from abc import ABCMeta, abstractmethod


class _AbcDirectoryHandler(metaclass=ABCMeta):
    @abstractmethod
    def send_error(self, code, message=None, explain=None):
        ...

    @abstractmethod
    def translate_path(self, path):
        ...

    @abstractmethod
    def _render_directory(self, path, add_to_context: dict = None):
        ...


class _UploadInfoCheck(_AbcDirectoryHandler, metaclass=ABCMeta):
    POST = 'POST'
    _REQUEST_METHOD_ENVIRON_KEY = 'REQUEST_METHOD'
    _CONTENT_TYPE_ENVIRON_KEY = 'CONTENT_TYPE'
    PARSE_FAIL_ERR_TEXT = 'Failed to parse multipart form data'
    SAVE_FAIL_ERR_TEXT = 'Error saving uploaded file'

    def __init__(self):
        self.logger = None
        self.path = None
        self.headers = {}

    @property
    def field_storage_environ(self):
        return {
            self.__class__._REQUEST_METHOD_ENVIRON_KEY:
                self.__class__.POST,
            self.__class__._CONTENT_TYPE_ENVIRON_KEY:
                self.headers.get('Content-Type')
        }

    @staticmethod
    def _safe_filename(name: str) -> str:
        base = os.path.basename(name)
        # Replace path separators and risky characters
        safe = ''.join(c for c in base if c.isalnum() or c in (' ', '.', '-', '_'))
        return safe or 'upload.bin'

    @staticmethod
    def _unique_path(directory: str, filename: str) -> str:
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

    def _check_content_type(self):
        ctype, pdict = cgi.parse_header(self.headers.get('Content-Type', ''))
        if ctype != 'multipart/form-data':
            self.send_error(400, "Unsupported Content-Type")
            return
        return pdict

    def _get_and_log_upload_fail_type(self, exception, was_parse=True,
                                      was_save=False):
        if was_parse:
            self.logger.exception(f"{self.__class__.PARSE_FAIL_ERR_TEXT}: {exception}")
        elif was_save:
            self.logger.exception(f"{self.__class__.SAVE_FAIL_ERR_TEXT}: {exception}")
        elif was_save and was_parse:
            self.logger.exception("'was_save' and 'was_parse' cannot be true at the same time")
            raise AttributeError("'was_save' and 'was_parse' cannot be true at the same time")
        else:
            self.logger.exception(exception)

    def _check_upload_path_is_dir(self):
        directory = self.translate_path(self.path)
        if not os.path.isdir(directory):
            self.send_error(400, "Upload path is not a directory")
            return
        return directory


class UploadHandlerMixin(_UploadInfoCheck, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self.headers = {}
        self.rfile = None
        self.path = None
        self.logger = None

    def _get_upload_success_msg(self, filename, data_len: int):
        ...

    def _get_upload_fail_msg(self, exception):
        ...

    def _handle_upload_failed(self, exception, **kwargs):
        self._get_and_log_upload_fail_type(exception, **kwargs)
        msg = self._get_upload_fail_msg(exception)
        return self._render_directory(self.translate_path(self.path), {'message': msg})

    def _handle_upload_success(self, filename, data_len: int, dest_path, directory):
        msg = self._get_upload_success_msg(filename, data_len)
        self.logger.info(f"Uploaded file saved to {dest_path}")
        return self._render_directory(directory, {'message': msg})

    def _get_fieldstorage_field(self):
        # Use FieldStorage to parse the incoming data stream
        try:
            form = cgi.FieldStorage(fp=self.rfile,
                                    headers=self.headers,
                                    environ=self.field_storage_environ)
        except Exception as e:
            self._handle_upload_failed(e)
            form = None
        try:
            field = form['file']
        except KeyError as e:
            self.logger.error(e, exc_info=True)
            field = None

        if not getattr(field, 'filename', None):
            return self._handle_upload_failed('No file provided.')
        return field

    def _write_file_to_stream(self, dest_path, field, filename, directory):
        try:
            with open(dest_path, 'wb') as out:
                data = field.file.read()
                out.write(data)
            return self._handle_upload_success(filename, len(data), dest_path, directory)
        except Exception as e:
            return self._handle_upload_failed(e, was_save=True)

    def do_POST(self):
        pdict = self._check_content_type()
        if not pdict:
            return None

        pdict['boundary'] = (pdict['boundary'].encode()
                             if isinstance(pdict.get('boundary'), str)
                             else pdict.get('boundary'))

        field = self._get_fieldstorage_field()

        directory = self._check_upload_path_is_dir()

        filename = self._safe_filename(field.filename)
        dest_path = self._unique_path(directory, filename)

        render = self._write_file_to_stream(dest_path, field, filename, directory)
        return render
