r"""Contain utilities for optional tomli dependency."""

from __future__ import annotations

__all__ = ["check_tomli", "is_tomli_available", "raise_tomli_missing_error", "tomli_available"]

from functools import lru_cache
from typing import TYPE_CHECKING, Any, NoReturn, TypeVar

from feu.utils.imports.universal import (
    decorator_package_available,
    package_available,
    raise_package_missing_error,
)

if TYPE_CHECKING:
    from collections.abc import Callable

F = TypeVar("F", bound="Callable[..., Any]")


def check_tomli() -> None:
    r"""Check if the ``tomli`` package is installed.

    Raises:
        RuntimeError: if the ``tomli`` package is not installed.

    Example:
        ```pycon
        >>> from feu.utils.imports import check_tomli
        >>> check_tomli()

        ```
    """
    if not is_tomli_available():
        raise_tomli_missing_error()


@lru_cache
def is_tomli_available() -> bool:
    r"""Indicate if the ``tomli`` package is installed or not.

    Returns:
        ``True`` if ``tomli`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from feu.utils.imports import is_tomli_available
        >>> is_tomli_available()

        ```
    """
    return package_available("tomli")


def tomli_available(fn: F) -> F:
    r"""Implement a decorator to execute a function only if ``tomli``
    package is installed.

    Args:
        fn: The function to execute.

    Returns:
        A wrapper around ``fn`` if ``tomli`` package is installed,
            otherwise ``None``.

    Example:
        ```pycon
        >>> from feu.utils.imports import tomli_available
        >>> @tomli_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_tomli_available)


def raise_tomli_missing_error() -> NoReturn:
    r"""Raise a RuntimeError to indicate the ``tomli`` package is
    missing."""
    raise_package_missing_error("tomli", "tomli")
