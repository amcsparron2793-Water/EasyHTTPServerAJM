import sys


def is_frozen() -> bool:
    """
    Return True if the application appears to be running from a frozen/packaged executable.

    This works with PyInstaller, cx_Freeze, py2exe, and most similar tools
    that set sys.frozen.
    """
    return bool(getattr(sys, "frozen", False))


from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder.template_asset_helper import AssetHelper, UploadAssetHelper
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder.mixins import FormatDirectoryEntryMixin
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder.template_wrappers import TableWrapperHelper, HTMLWrapperHelper
from EasyHTTPServerAJM.Helpers.HtmlTemplateBuilder.html_template_builder import (HTMLTemplateBuilder,
                                                                                 HTMLTemplateBuilderUpload)
