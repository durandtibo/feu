r"""Contain utilities for optional urllib3 dependency."""

from __future__ import annotations

__all__ = [
    "check_urllib3",
    "is_urllib3_available",
    "raise_urllib3_missing_error",
    "urllib3_available",
]

from functools import cache
from typing import TYPE_CHECKING, Any, Never, TypeVar

from feu.imports.universal import (
    decorator_package_available,
    is_package_available,
    raise_package_missing_error,
)

if TYPE_CHECKING:
    from collections.abc import Callable

F = TypeVar("F", bound="Callable[..., Any]")


def check_urllib3() -> None:
    r"""Check if the ``urllib3`` package is installed.

    Raises:
        RuntimeError: if the ``urllib3`` package is not installed.

    Example:
        ```pycon
        >>> from feu.imports import check_urllib3
        >>> check_urllib3()

        ```
    """
    if not is_urllib3_available():
        raise_urllib3_missing_error()


@cache
def is_urllib3_available() -> bool:
    r"""Indicate if the ``urllib3`` package is installed or not.

    Returns:
        ``True`` if ``urllib3`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from feu.imports import is_urllib3_available
        >>> is_urllib3_available()

        ```
    """
    return is_package_available("urllib3")


def urllib3_available(fn: F) -> F:
    r"""Implement a decorator to execute a function only if ``urllib3``
    package is installed.

    Args:
        fn: The function to execute.

    Returns:
        A wrapper around ``fn``. When the wrapper is called, it
            executes ``fn`` and returns its output if the ``urllib3``
            package is installed, otherwise it does nothing and
            returns ``None``.

    Example:
        ```pycon
        >>> from feu.imports import urllib3_available
        >>> @urllib3_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_urllib3_available)


def raise_urllib3_missing_error() -> Never:
    r"""Raise a RuntimeError to indicate the ``urllib3`` package is
    missing.

    Raises:
        RuntimeError: Always raised to indicate the package is missing.
    """
    raise_package_missing_error("urllib3", "urllib3")
