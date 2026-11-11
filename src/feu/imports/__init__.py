r"""Contain utilities to manage optional dependencies.

This is a port of ``coola.utils.imports``: ``package.py`` (availability
checks and ``MissingPackageError``), ``optional.py`` (the optional
libraries of ``feu``) and ``lazy.py`` (``lazy_exports``).
"""

from __future__ import annotations

__all__ = [
    "MissingPackageError",
    "availability_cache",
    "check_click",
    "check_git",
    "check_package",
    "check_requests",
    "check_rich",
    "clear_availability_caches",
    "is_click_available",
    "is_git_available",
    "is_module_available",
    "is_package_available",
    "is_requests_available",
    "is_rich_available",
    "lazy_exports",
    "module_available",
    "package_available",
    "raise_package_missing_error",
]

from feu.imports.lazy import lazy_exports
from feu.imports.optional import (
    check_click,
    check_git,
    check_requests,
    check_rich,
    is_click_available,
    is_git_available,
    is_requests_available,
    is_rich_available,
)
from feu.imports.package import (
    MissingPackageError,
    availability_cache,
    check_package,
    clear_availability_caches,
    is_module_available,
    is_package_available,
    module_available,
    package_available,
    raise_package_missing_error,
)
