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
        # internal storage for all “resolved” flags
        self._resolved_flags = {vt: False for vt in PathValidationType}

        self.candidate_path: Optional[Union[str, Path]] = kwargs.get('candidate_path', None)
        self.candidate_path_validation_type = kwargs.get('candidate_path_validation_type',
                                                         PathValidationType.FILE)

    def resolve(self):
        """Calculate resolution flags for the current candidate_path."""
        self._check_for_path_set()
        p: Path = self.candidate_path

        # Reset all flags first
        for vt in PathValidationType:
            self.is_resolved_to_attr(vt, False)

        # Now set the appropriate flags based on the filesystem and type
        if p.exists():
            if p.is_dir():
                self.is_resolved_to_dir = True
            elif p.is_file():
                # basic file; further refine by extension
                ext = p.suffix.lower()
                print(ext)
                if ext == ".html":
                    self.is_resolved_to_html = True
                elif ext == ".svg":
                    self.is_resolved_to_svg = True
                elif ext == ".css":
                    self.is_resolved_to_css = True
                else:
                    # generic file
                    self.is_resolved_to_file = True

    def is_resolved_to_attr(self, vt: PathValidationType, value: bool):
        """Helper for resetting flags by enum."""
        attr_name = f"is_resolved_to_{vt.name.lower()}"
        setattr(self, attr_name, value)

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

    def _name_to_validation_type(self, attr_name: str):
        prefix = "is_resolved_to_"
        if attr_name.startswith(prefix):
            suffix = attr_name[len(prefix):].upper()
            for vt in PathValidationType:
                if vt.name == suffix:
                    return vt
        return None

    def __getattr__(self, name: str):
        print(name)
        vt = self._name_to_validation_type(name)
        if vt is not None:
            # expose a boolean attribute like .is_resolved_to_file
            return self._resolved_flags[vt]
        # normal AttributeError for anything else
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def __setattr__(self, name: str, value):
        # handle dynamic “is_resolved_to_*” attributes
        vt = None
        if not name.startswith("_"):  # skip internal attributes
            vt = self._name_to_validation_type(name)
        else:
            self.logger.debug(f"skipping internal attribute {name}")

        if vt is not None:
            self._resolved_flags[vt] = bool(value)
        else:
            super().__setattr__(name, value)

    def _check_for_path_set(self):
        if self.candidate_path is None:
            raise CandidatePathNotSetError("candidate_path must be set before using this class")

    def validate(self):
        vt = self.candidate_path_validation_type
        if vt is None:
            raise ValueError("candidate_path_validation_type is not set")

        # dynamic attribute name based on enum
        # e.g., PathValidationType.FILE -> "is_resolved_to_file"
        attr_name = f"is_resolved_to_{vt.name.lower()}"
        return getattr(self, attr_name)