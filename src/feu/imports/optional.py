r"""Contain the availability checks of the optional libraries.

``is_<package>_available`` indicates if a library can be imported and
``check_<package>`` raises a ``MissingPackageError`` if it cannot. The
libraries are the optional dependencies of ``feu``: ``click``, ``git``
(installed with ``gitpython``), ``requests`` and ``rich``.
"""

from __future__ import annotations

__all__ = [
    "check_click",
    "check_git",
    "check_requests",
    "check_rich",
    "is_click_available",
    "is_git_available",
    "is_requests_available",
    "is_rich_available",
]

from feu.imports.package import availability_cache, module_available, raise_package_missing_error


@availability_cache
def is_click_available() -> bool:
    r"""Indicate if the ``click`` package is installed and can be
    imported.

    Returns:
        ``True`` if ``click`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from feu.imports import is_click_available
        >>> isinstance(is_click_available(), bool)
        True

        ```
    """
    return module_available("click")


def check_click() -> None:
    r"""Check if the ``click`` package is installed.

    Raises:
        MissingPackageError: if the ``click`` package is not installed.
            The message gives the command to install it.

    Example:
        ```pycon
        >>> from feu.imports import check_click
        >>> check_click()  # doctest: +SKIP

        ```
    """
    if not is_click_available():
        raise_package_missing_error("click")


@availability_cache
def is_git_available() -> bool:
    r"""Indicate if the ``git`` package is installed and can be imported.

    Returns:
        ``True`` if ``git`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from feu.imports import is_git_available
        >>> isinstance(is_git_available(), bool)
        True

        ```
    """
    return module_available("git")


def check_git() -> None:
    r"""Check if the ``git`` package is installed.

    Raises:
        MissingPackageError: if the ``git`` package is not installed.
            The message gives the command to install it (``gitpython``).

    Example:
        ```pycon
        >>> from feu.imports import check_git
        >>> check_git()  # doctest: +SKIP

        ```
    """
    if not is_git_available():
        raise_package_missing_error("git", install="gitpython")


@availability_cache
def is_requests_available() -> bool:
    r"""Indicate if the ``requests`` package is installed and can be
    imported.

    Returns:
        ``True`` if ``requests`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from feu.imports import is_requests_available
        >>> isinstance(is_requests_available(), bool)
        True

        ```
    """
    return module_available("requests")


def check_requests() -> None:
    r"""Check if the ``requests`` package is installed.

    Raises:
        MissingPackageError: if the ``requests`` package is not installed.
            The message gives the command to install it.

    Example:
        ```pycon
        >>> from feu.imports import check_requests
        >>> check_requests()  # doctest: +SKIP

        ```
    """
    if not is_requests_available():
        raise_package_missing_error("requests")


@availability_cache
def is_rich_available() -> bool:
    r"""Indicate if the ``rich`` package is installed and can be
    imported.

    Returns:
        ``True`` if ``rich`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from feu.imports import is_rich_available
        >>> isinstance(is_rich_available(), bool)
        True

        ```
    """
    return module_available("rich")


def check_rich() -> None:
    r"""Check if the ``rich`` package is installed.

    Raises:
        MissingPackageError: if the ``rich`` package is not installed.
            The message gives the command to install it.

    Example:
        ```pycon
        >>> from feu.imports import check_rich
        >>> check_rich()  # doctest: +SKIP

        ```
    """
    if not is_rich_available():
        raise_package_missing_error("rich")
