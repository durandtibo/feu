r"""Contain utilities for optional git dependency."""

from __future__ import annotations

__all__ = ["check_git", "git_available", "is_git_available", "raise_git_missing_error"]

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


def check_git() -> None:
    r"""Check if the ``git`` package is installed.

    Raises:
        RuntimeError: if the ``git`` package is not installed.

    Example:
        ```pycon
        >>> from feu.utils.imports import check_git
        >>> check_git()

        ```
    """
    if not is_git_available():
        raise_git_missing_error()


@lru_cache
def is_git_available() -> bool:
    r"""Indicate if the ``git`` package is installed or not.

    Returns:
        ``True`` if ``git`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from feu.utils.imports import is_git_available
        >>> is_git_available()

        ```
    """
    return package_available("git")


def git_available(fn: F) -> F:
    r"""Implement a decorator to execute a function only if ``git``
    package is installed.

    Args:
        fn: The function to execute.

    Returns:
        A wrapper around ``fn`` if ``git`` package is installed,
            otherwise ``None``.

    Example:
        ```pycon
        >>> from feu.utils.imports import git_available
        >>> @git_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_git_available)


def raise_git_missing_error() -> NoReturn:
    r"""Raise a RuntimeError to indicate the ``git`` package is
    missing."""
    raise_package_missing_error("git", "gitpython")
