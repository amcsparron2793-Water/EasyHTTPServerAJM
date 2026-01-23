from abc import abstractmethod, ABC
from logging import getLogger
from pathlib import Path
from typing import Optional, Union

from EasyHTTPServerAJM.Helpers import PathValidationType


class CandidatePathNotSetError(Exception):
    ...


class PathFlagResolver(ABC):
    """
    Resolves flags based on the attributes of a given file system path.

    This abstract base class provides functionality to evaluate a candidate file
    system path and determine its characteristics by setting specific flags. It
    is designed to be subclassed to implement application-specific logic for
    path-related validation and resolution. The flags indicate properties
    such as whether the path is a directory, a file, or specific file types
    (e.g., HTML, SVG, CSS).

    :ivar logger: Logger instance used for logging information, debug messages, and errors.
    :type logger: logging.Logger
    """
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger', getLogger(__name__))
        # internal storage for all “resolved” flags
        self._resolved_flags = {vt: False for vt in PathValidationType}

    @abstractmethod
    def _check_for_path_set(self):
        raise NotImplementedError("Subclasses must implement this method")

    @property
    @abstractmethod
    def candidate_path(self):
        raise NotImplementedError("Subclasses must implement this property")

    def _pre_resolve(self):
        self._check_for_path_set()
        p: Path = self.candidate_path
        return p

    def _reset_flags(self):
        # Reset all flags first
        for vt in PathValidationType:
            self.set_is_resolved_to_attr(vt, False)
        self.logger.info("Reset all \'is_resolved_to_*\' flags")

    def _resolve_existing_path(self, p: Path):
        if p.is_dir():
            self.logger.debug(f"{p} is a directory")
            self._resolve_sub_dir(p)
        elif p.is_file():
            self.logger.debug(f"{p} is a file")
            self._resolve_sub_file(p)

    def _resolve_sub_file(self, p: Path):
        # basic file; further refine by extension
        ext = p.suffix.lower()
        if ext == ".html":
            self.is_resolved_to_html = True
        elif ext == ".svg":
            self.is_resolved_to_svg = True
        elif ext == ".css":
            self.is_resolved_to_css = True
        else:
            # generic file
            self.is_resolved_to_file = True
        self.logger.debug(f"{p} is a {ext} file")

    def _resolve_sub_dir(self, p: Path):
        # this check is redundant, but it's here for completeness
        if p.is_dir():
            self.is_resolved_to_dir = True

    # noinspection PyAttributeOutsideInit
    def resolve_flags(self):
        """Calculate resolution flags for the current candidate_path."""
        p = self._pre_resolve()
        self._reset_flags()

        # Now set the appropriate flags based on the filesystem and type
        if p.exists():
            self.logger.debug(f"{p} exists")
            self._resolve_existing_path(p)
        else:
            if p.suffix.lstrip('.') != PathValidationType.HTML.value:
                self.logger.error(f"{p} does not exist, could not resolve")
            else:
                self.logger.critical(f"{p} does not exist, could not resolve")
                #raise FileNotFoundError(f"{p} does not exist") from None

    def set_is_resolved_to_attr(self, vt: PathValidationType, value: bool):
        """Helper for resetting flags by enum."""
        attr_name = f"is_resolved_to_{vt.name.lower()}"
        setattr(self, attr_name, value)


class PathValidator(PathFlagResolver):
    """
    Responsible for validating paths and dynamically resolving associated validation attributes.

    This class extends `PathFlagResolver` to handle validation and dynamic resolution of paths
    and their corresponding validation types. It utilizes a logger for debugging and tracking
    internal processes. The primary use of this class is to set, validate, and resolve paths
    and their attributes dynamically, based on predefined validation types.

    :ivar candidate_path: Candidate path that should be resolved and validated.
    :type candidate_path: Optional[Union[str, Path]]
    :ivar candidate_path_validation_type: Validation type for the candidate path.
    :type candidate_path_validation_type: Union[str, PathValidationType]
    """
    def __init__(self, **kwargs):
        self.logger = kwargs.pop('logger', getLogger(__name__))
        super().__init__(logger=self.logger, **kwargs)

        self._candidate_path = None
        self._candidate_path_validation_type = None

        self.candidate_path: Optional[Union[str, Path]] = kwargs.get('candidate_path', None)
        # noinspection PyTypeChecker
        self.candidate_path_validation_type = kwargs.get('candidate_path_validation_type',
                                                         PathValidationType.FILE)

    def __getattr__(self, name: str):
        """ this is only called if the attribute is not found using __getattribute__."""
        vt = self._name_to_validation_type(name)
        if vt is not None:
            # expose a boolean attribute like .is_resolved_to_file
            return self._resolved_flags[vt]
        # normal AttributeError for anything else
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def __setattr__(self, name: str, value):
        # make sure logger gets set first so it can handle errors etc
        if 'logger' in name:
            super().__setattr__(name, value)
            return

        # handle dynamic “is_resolved_to_*” attributes
        # vt stands for 'validation type'
        vt = None
        if not name.startswith("_"):  # skip internal attributes i.e. _resolved_flags
            vt = self._name_to_validation_type(name)
        else:
            self.logger.debug(f"skipping internal attribute {name}")

        if vt is not None:
            self._resolved_flags[vt] = bool(value)
        # handle normal attributes
        else:
            super().__setattr__(name, value)

    def _check_for_path_set(self):
        if self.candidate_path is None:
            raise CandidatePathNotSetError("candidate_path must be set before using this class")

    @staticmethod
    def _resolve_to_full_path(candidate_path: Union[str, Path]) -> Path:
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
            self._candidate_path = self._resolve_to_full_path(value)

    @property
    def candidate_path_validation_type(self):
        return self._candidate_path_validation_type

    @candidate_path_validation_type.setter
    def candidate_path_validation_type(self, value: Union[str, PathValidationType]):
        self._candidate_path_validation_type = PathValidationType(value)

    def _name_to_validation_type(self, attr_name: str):
        prefix = "is_resolved_to_"
        if attr_name.startswith(prefix):
            self.logger.debug(f"Found prefix {prefix} in {attr_name}")
            suffix = attr_name[len(prefix):].upper()
            for vt in PathValidationType:
                if vt.name == suffix:
                    self.logger.debug(f"Found validation type {vt} for {attr_name}")
                    return vt
        self.logger.debug(f"No validation type found for {attr_name}")
        return None

    def validate(self):
        vt = self.candidate_path_validation_type
        if vt is None:
            raise ValueError("candidate_path_validation_type is not set")

        # dynamic attribute name based on enum
        # e.g., PathValidationType.FILE -> "is_resolved_to_file"
        attr_name = f"is_resolved_to_{vt.name.lower()}"
        return getattr(self, attr_name)
