r"""Contain utilities to manage optional dependencies."""

from __future__ import annotations

__all__ = [
    "check_package",
    "decorator_package_available",
    "module_available",
    "package_available",
    "raise_package_missing_error",
]


from feu.utils.imports.universal import (
    check_package,
    decorator_package_available,
    module_available,
    package_available,
    raise_package_missing_error,
)
