from logging import getLogger
from pathlib import Path
from typing import Optional, Union

from EasyHTTPServerAJM.Helpers import PathValidationType


class CandidatePathNotSetError(Exception):
    ...


class PathValidator:
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger', getLogger(__name__))
        self._candidate_path = None
        self._candidate_path_validation_type = None

        self.candidate_path: Optional[Union[str, Path]] = kwargs.get('candidate_path', None)
        self.candidate_path_validation_type = kwargs.get('candidate_path_validation_type',
                                                         PathValidationType.FILE)

    @staticmethod
    def _resolve_path(candidate_path: Union[str, Path]) -> Path:
        if isinstance(candidate_path, str):
            candidate_path = Path(candidate_path).resolve()
        elif isinstance(candidate_path, Path):
            candidate_path = candidate_path.resolve()
        else:
            raise ValueError(f"{candidate_path} is not a valid path")
        return candidate_path

    @property
    def candidate_path(self):
        return self._candidate_path

    @candidate_path.setter
    def candidate_path(self, value: Union[str, Path]):
        if value is None:
            self.logger.debug(f"candidate_path is None, candidate_path must be still be set")
            self._candidate_path = None
        else:
            self._candidate_path = self._resolve_path(value)

    @property
    def candidate_path_validation_type(self):
        return self._candidate_path_validation_type

    @candidate_path_validation_type.setter
    def candidate_path_validation_type(self, value: Union[str, PathValidationType]):
        self._candidate_path_validation_type = PathValidationType(value)

    @property
    def is_resolved_to_dir(self) -> bool:
        self._check_for_path_set()
        if self.candidate_path.is_dir():
            return True
        else:
            raise ValueError(f"{self.candidate_path} is not a valid directory")

    @property
    def is_resolved_to_file(self) -> bool:
        self._check_for_path_set()
        if self.candidate_path.is_file():
            return True
        else:
            raise ValueError(f"{self.candidate_path} is not a valid file")

    def _is_resolved_to_specific_file(self, file_suffix: str) -> bool:
        file_suffix = file_suffix.lstrip('.')
        c_path_suffix = self.candidate_path.suffix.lstrip('.')
        self._check_for_path_set()
        if self.candidate_path.is_file() and c_path_suffix == file_suffix:
            return True
        else:
            raise ValueError(f"{self.candidate_path} is not a valid {file_suffix} file")

    @property
    def is_resolved_to_html(self) -> bool:
        self._check_for_path_set()
        return self._is_resolved_to_specific_file('html')

    @property
    def is_resolved_to_svg(self) -> bool:
        self._check_for_path_set()
        return self._is_resolved_to_specific_file('svg')

    @property
    def is_resolved_to_css(self) -> bool:
        self._check_for_path_set()
        return self._is_resolved_to_specific_file('css')

    def _check_for_path_set(self):
        if self.candidate_path is None:
            raise CandidatePathNotSetError("candidate_path must be set before using this class")

    def validate(self):
        if self.candidate_path_validation_type == PathValidationType.FILE:
            return self.is_resolved_to_file
        elif self.candidate_path_validation_type == PathValidationType.DIR:
            return self.is_resolved_to_dir
        elif self.candidate_path_validation_type == PathValidationType.HTML:
            return self.is_resolved_to_html
        elif self.candidate_path_validation_type == PathValidationType.SVG:
            return self.is_resolved_to_svg
        elif self.candidate_path_validation_type == PathValidationType.CSS:
            return self.is_resolved_to_css
        else:
            raise ValueError(f"{self.candidate_path_validation_type} is not a valid validation type")