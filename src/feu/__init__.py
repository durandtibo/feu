r"""Root package of ``feu``."""

from __future__ import annotations

__all__ = [
    "compare_version",
    "get_package_version",
    "install_package",
    "is_module_available",
    "is_package_available",
]

from feu.imports import is_module_available, is_package_available
from feu.install import install_package
from feu.version import compare_version, get_package_version
