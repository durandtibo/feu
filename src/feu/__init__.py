from __future__ import annotations

__all__ = [
    "get_package_version",
    "is_module_available",
    "is_package_available",
]

from feu.imports import is_module_available, is_package_available
from feu.version import get_package_version
