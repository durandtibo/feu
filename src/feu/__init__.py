from __future__ import annotations

__all__ = [
    "compare_version",
    "get_package_version",
    "is_module_available",
    "is_package_available",
]

from feu.imports import is_module_available, is_package_available
from feu.version import compare_version, get_package_version
