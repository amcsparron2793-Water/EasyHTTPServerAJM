from logging import getLogger
from pathlib import Path
from typing import Optional, Union, Tuple

from EasyHTTPServerAJM.Helpers import PathValidator, PathValidationType


class AssetHelper:
    """
    Provides functionality to manage and validate paths for assets, templates, and related resources.

    This class serves as a utility to handle file paths associated with various elements like templates,
    assets, and stylesheets. It validates paths using an injected path validation class and provides
    structured access to these paths through class properties.

    :ivar DEFAULT_ASSETS_PATH: Default path to the assets directory.
    :type DEFAULT_ASSETS_PATH: Path
    :ivar DEFAULT_TEMPLATES_PATH: Default path to the templates directory.
    :type DEFAULT_TEMPLATES_PATH: Path
    :ivar DEFAULT_HTML_TEMPLATE_PATH: Default path to the HTML template file.
    :type DEFAULT_HTML_TEMPLATE_PATH: Path
    :ivar DEFAULT_BACK_SVG_PATH: Default path to the back SVG file.
    :type DEFAULT_BACK_SVG_PATH: Path
    :ivar DEFAULT_DIRECTORY_PAGE_CSS_PATH: Default path to the CSS file for directory pages.
    :type DEFAULT_DIRECTORY_PAGE_CSS_PATH: Path
    """
    DEFAULT_ASSETS_PATH = Path('../Misc_Project_Files/assets').resolve()
    DEFAULT_TEMPLATES_PATH = Path('../Misc_Project_Files/templates').resolve()
    DEFAULT_HTML_TEMPLATE_PATH = Path(DEFAULT_TEMPLATES_PATH, 'directory_page_template.html').resolve()
    DEFAULT_BACK_SVG_PATH = Path(DEFAULT_ASSETS_PATH, 'BackBoxWithText.svg').resolve()
    DEFAULT_DIRECTORY_PAGE_CSS_PATH = Path(DEFAULT_TEMPLATES_PATH, 'directory_page.css').resolve()

    def __init__(self, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        self.logger = kwargs.pop('logger', getLogger(__name__))
        self._templates_path = None
        self._html_template_path = None
        self._assets_path = None
        self._back_svg_path = None
        self._directory_page_css_path = None

        self.path_validator = kwargs.pop('path_validator_class', PathValidator)(**kwargs, logger=self.logger)
        self._set_paths(html_template_path, **kwargs)

    def _set_paths(self, html_template_path: Optional[Union[str, Path]] = None, **kwargs):
        # Each call passes (path, PathValidationType) plus the private attr name
        self._set_property(
            (kwargs.get('templates_path', self.__class__.DEFAULT_TEMPLATES_PATH), PathValidationType.DIR),
            "_templates_path",
        )
        self._set_property(
            (
                html_template_path
                if html_template_path is not None
                else self.__class__.DEFAULT_HTML_TEMPLATE_PATH,
                PathValidationType.HTML,
            ),
            "_html_template_path",
        )
        self._set_property(
            (kwargs.get('assets_path', self.__class__.DEFAULT_ASSETS_PATH), PathValidationType.DIR),
            "_assets_path",
        )
        self._set_property(
            (kwargs.get('back_svg_path', self.__class__.DEFAULT_BACK_SVG_PATH), PathValidationType.SVG),
            "_back_svg_path",
        )
        self._set_property(
            (
                kwargs.get(
                    'directory_page_css_path',
                    self.__class__.DEFAULT_DIRECTORY_PAGE_CSS_PATH,
                ),
                PathValidationType.CSS,
            ),
            "_directory_page_css_path",
        )
        self.logger.debug("Paths set")

    @property
    def templates_path(self) -> Optional[Path]:
        return self._templates_path

    @property
    def html_template_path(self) -> Optional[Path]:
        return self._html_template_path

    @property
    def assets_path(self) -> Optional[Path]:
        return self._assets_path

    @property
    def back_svg_path(self) -> Optional[Path]:
        return self._back_svg_path

    @property
    def directory_page_css_path(self) -> Optional[Path]:
        return self._directory_page_css_path

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
        self.path_validator.resolve_flags()
        if self.path_validator.validate():
            self.__setattr__(private_property_name, value[0])
            self.logger.debug(f"{private_property_name} set to {value[0]}")
        else:
            self.logger.error(f"Failed to set {private_property_name} to {value[0]} - did not validate")