r"""Contain utilities to manage optional dependencies."""

from __future__ import annotations

__all__ = [
    "check_click",
    "check_git",
    "check_package",
    "check_requests",
    "click_available",
    "decorator_package_available",
    "git_available",
    "is_click_available",
    "is_git_available",
    "is_requests_available",
    "module_available",
    "package_available",
    "raise_click_missing_error",
    "raise_git_missing_error",
    "raise_package_missing_error",
    "raise_requests_missing_error",
    "requests_available",
]

from feu.utils.imports.click import (
    check_click,
    click_available,
    is_click_available,
    raise_click_missing_error,
)
from feu.utils.imports.git import (
    check_git,
    git_available,
    is_git_available,
    raise_git_missing_error,
)
from feu.utils.imports.requests import (
    check_requests,
    is_requests_available,
    raise_requests_missing_error,
    requests_available,
)
from feu.utils.imports.universal import (
    check_package,
    decorator_package_available,
    module_available,
    package_available,
    raise_package_missing_error,
)
