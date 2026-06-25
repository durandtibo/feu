r"""Contain utilities to manage optional dependencies."""

from __future__ import annotations

__all__ = [
    "check_package",
    "check_tomli",
    "decorator_package_available",
    "is_tomli_available",
    "module_available",
    "package_available",
    "raise_package_missing_error",
    "raise_tomli_missing_error",
    "tomli_available",
]

from feu.utils.imports.tomli import (
    check_tomli,
    is_tomli_available,
    raise_tomli_missing_error,
    tomli_available,
)
from feu.utils.imports.universal import (
    check_package,
    decorator_package_available,
    module_available,
    package_available,
    raise_package_missing_error,
)
