r"""Contain utilities to manage optional dependencies."""

from __future__ import annotations

__all__ = [
    "check_click",
    "check_git",
    "check_package",
    "check_requests",
    "check_urllib3",
    "click_available",
    "decorator_package_available",
    "git_available",
    "is_click_available",
    "is_git_available",
    "is_module_available",
    "is_package_available",
    "is_requests_available",
    "is_urllib3_available",
    "raise_click_missing_error",
    "raise_git_missing_error",
    "raise_package_missing_error",
    "raise_requests_missing_error",
    "raise_urllib3_missing_error",
    "requests_available",
    "urllib3_available",
]

from feu.imports.click import (
    check_click,
    click_available,
    is_click_available,
    raise_click_missing_error,
)
from feu.imports.git import (
    check_git,
    git_available,
    is_git_available,
    raise_git_missing_error,
)
from feu.imports.requests import (
    check_requests,
    is_requests_available,
    raise_requests_missing_error,
    requests_available,
)
from feu.imports.universal import (
    check_package,
    decorator_package_available,
    is_module_available,
    is_package_available,
    raise_package_missing_error,
)
from feu.imports.urllib3 import (
    check_urllib3,
    is_urllib3_available,
    raise_urllib3_missing_error,
    urllib3_available,
)
