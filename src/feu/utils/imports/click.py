r"""Contain utilities for optional click dependency."""

from __future__ import annotations

__all__ = ["check_click", "click_available", "is_click_available", "raise_click_missing_error"]

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


def check_click() -> None:
    r"""Check if the ``click`` package is installed.

    Raises:
        RuntimeError: if the ``click`` package is not installed.

    Example:
        ```pycon
        >>> from feu.utils.imports import check_click
        >>> check_click()

        ```
    """
    if not is_click_available():
        raise_click_missing_error()


@lru_cache
def is_click_available() -> bool:
    r"""Indicate if the ``click`` package is installed or not.

    Returns:
        ``True`` if ``click`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from feu.utils.imports import is_click_available
        >>> is_click_available()

        ```
    """
    return package_available("click")


def click_available(fn: F) -> F:
    r"""Implement a decorator to execute a function only if ``click``
    package is installed.

    Args:
        fn: The function to execute.

    Returns:
        A wrapper around ``fn`` if ``click`` package is installed,
            otherwise ``None``.

    Example:
        ```pycon
        >>> from feu.utils.imports import click_available
        >>> @click_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_click_available)


def raise_click_missing_error() -> NoReturn:
    r"""Raise a RuntimeError to indicate the ``click`` package is
    missing."""
    raise_package_missing_error("click", "click")
