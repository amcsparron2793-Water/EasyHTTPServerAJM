from logging import getLogger
from pathlib import Path
from typing import Optional, Union, Tuple

from EasyHTTPServerAJM.Helpers import PathValidator, PathValidationType


class AssetHelper:
    DEFAULT_ASSETS_PATH = Path('../Misc_Project_Files/assets').resolve()
    DEFAULT_TEMPLATES_PATH = Path('../Misc_Project_Files/templates').resolve()
    DEFAULT_HTML_TEMPLATE_PATH = Path(DEFAULT_TEMPLATES_PATH, 'directory_page_template.html').resolve()
    DEFAULT_BACK_SVG_PATH = Path(DEFAULT_ASSETS_PATH, 'BackBoxWithText.svg').resolve()

    def __init__(self, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        self.logger = kwargs.pop('logger', getLogger(__name__))
        self._templates_path = None
        self._html_template_path = None
        self._assets_path = None
        self._back_svg_path = None
        self.path_validator = PathValidator(**kwargs, logger=self.logger)
        self._set_paths(html_template_path, **kwargs)

    def _set_paths(self, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        self.templates_path = (kwargs.get('templates_path', self.__class__.DEFAULT_TEMPLATES_PATH),
                               PathValidationType.DIR)
        self.html_template_path = ((html_template_path if html_template_path is not None
                                    else self.__class__.DEFAULT_HTML_TEMPLATE_PATH), PathValidationType.HTML)
        self.assets_path = (kwargs.get('assets_path', self.__class__.DEFAULT_ASSETS_PATH), PathValidationType.DIR)
        self.back_svg_path = (kwargs.get('back_svg_path', self.__class__.DEFAULT_BACK_SVG_PATH), PathValidationType.SVG)
        self.logger.debug("Paths set")

    def set_validator_paths(self, **kwargs):
        self.path_validator.candidate_path = kwargs.get('candidate_path', None)
        self.path_validator.candidate_path_validation_type = kwargs.get('candidate_path_validation_type',
                                                                        PathValidationType.FILE)
        self.logger.debug(f"SET Candidate path: {self.path_validator.candidate_path} "
                          f"with validation type: {self.path_validator.candidate_path_validation_type}")

    def _set_property(self, value: Tuple[Union[str, Path], PathValidationType],
                      private_property_name: str):
        self.set_validator_paths(candidate_path=value[0],
                                 candidate_path_validation_type=value[1])
        if self.path_validator.validate():
            self.__setattr__(private_property_name, value[0])
            self.logger.debug(f"{private_property_name} set to {value[0]}")

    @property
    def templates_path(self):
        return self._templates_path

    @templates_path.setter
    def templates_path(self, value: Tuple[Union[str, Path], PathValidationType]):
        self._set_property(value, '_templates_path')

    @property
    def html_template_path(self):
        return self._html_template_path

    @html_template_path.setter
    def html_template_path(self, value: Tuple[Union[str, Path], PathValidationType]):
        self._set_property(value, '_html_template_path')

    @property
    def assets_path(self):
        return self._assets_path

    @assets_path.setter
    def assets_path(self, value: Tuple[Union[str, Path], PathValidationType]):
        self._set_property(value, '_assets_path')

    @property
    def back_svg_path(self):
        return self._back_svg_path

    @back_svg_path.setter
    def back_svg_path(self, value: Tuple[Union[str, Path], PathValidationType]):
        self._set_property(value, '_back_svg_path')