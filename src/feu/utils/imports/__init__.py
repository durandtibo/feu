r"""Contain utilities to manage optional dependencies."""

from __future__ import annotations

__all__ = [
    "check_click",
    "check_package",
    "click_available",
    "decorator_package_available",
    "is_click_available",
    "module_available",
    "package_available",
    "raise_click_missing_error",
    "raise_package_missing_error",
]

from feu.utils.imports.click import (
    check_click,
    click_available,
    is_click_available,
    raise_click_missing_error,
)
from feu.utils.imports.universal import (
    check_package,
    decorator_package_available,
    module_available,
    package_available,
    raise_package_missing_error,
)
