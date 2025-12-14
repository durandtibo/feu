r"""Root package of ``feu``."""

from __future__ import annotations

__all__ = [
    "compare_version",
    "get_package_version",
    "install_package",
    "install_package_closest_version",
    "is_module_available",
    "is_package_available",
]

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as metadata_version

from feu.imports import is_module_available, is_package_available
from feu.install import install_package, install_package_closest_version
from feu.version import compare_version, get_package_version

try:
    __version__ = metadata_version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed, fallback if needed
    __version__ = "0.0.0"
