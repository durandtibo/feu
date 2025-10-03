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

from feu.imports import is_module_available, is_package_available
from feu.install import install_package, install_package_closest_version
from feu.version import compare_version, get_package_version
