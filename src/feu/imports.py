r"""Contain to check if a package or module is available."""

from __future__ import annotations

__all__ = [
    "check_click",
    "check_git",
    "check_requests",
    "check_urllib3",
    "is_click_available",
    "is_git_available",
    "is_module_available",
    "is_package_available",
    "is_requests_available",
    "is_urllib3_available",
    "raise_error_click_missing",
    "raise_error_git_missing",
    "raise_error_requests_missing",
    "raise_error_urllib3_missing",
]

from contextlib import suppress
from functools import lru_cache
from importlib import import_module
from importlib.util import find_spec
from typing import NoReturn


@lru_cache
def is_package_available(package: str) -> bool:
    r"""Check if a package is available.

    Args:
        package: The package name to check.

    Returns:
        ``True`` if the package is available, otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu import is_package_available
    >>> is_package_available("os")
    True
    >>> is_package_available("os.path")
    True
    >>> is_package_available("my_missing_package")
    False

    ```
    """
    with suppress(Exception):
        return find_spec(package) is not None
    return False


@lru_cache
def is_module_available(module: str) -> bool:
    r"""Check if a module path is available.

    Args:
        module: The module to check.

    Example usage:

    ```pycon

    >>> from feu import is_module_available
    >>> is_module_available("os")
    True
    >>> is_module_available("os.path")
    True
    >>> is_module_available("missing.module")
    False

    ```
    """
    if not is_package_available(str(module).split(".", maxsplit=1)[0]):
        return False
    try:
        import_module(module)
    except (ImportError, ModuleNotFoundError):
        return False
    return True


#################
#     click     #
#################


@lru_cache
def is_click_available() -> bool:
    r"""Indicate if the ``click`` package is installed or not.

    Returns:
        ``True`` if ``click`` is available otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.imports import is_click_available
    >>> is_click_available()

    ```
    """
    return is_package_available("click")


def check_click() -> None:
    r"""Check if the ``click`` package is installed.

    Raises:
        RuntimeError: if the ``click`` package is not installed.

    Example usage:

    ```pycon

    >>> from feu.imports import check_click
    >>> check_click()

    ```
    """
    if not is_click_available():
        raise_error_click_missing()


def raise_error_click_missing() -> NoReturn:
    r"""Raise a RuntimeError to indicate the ``click`` package is
    missing."""
    msg = (
        "'click' package is required but not installed. "
        "You can install 'click' package with the command:\n\n"
        "pip install click\n"
    )
    raise RuntimeError(msg)


###############
#     git     #
###############


@lru_cache
def is_git_available() -> bool:
    r"""Indicate if the ``git`` package is installed or not.

    Returns:
        ``True`` if ``git`` is available otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.imports import is_git_available
    >>> is_git_available()

    ```
    """
    return is_package_available("git")


def check_git() -> None:
    r"""Check if the ``git`` package is installed.

    Raises:
        RuntimeError: if the ``git`` package is not installed.

    Example usage:

    ```pycon

    >>> from feu.imports import check_git
    >>> check_git()

    ```
    """
    if not is_git_available():
        raise_error_git_missing()


def raise_error_git_missing() -> NoReturn:
    r"""Raise a RuntimeError to indicate the ``git`` package is
    missing."""
    msg = (
        "'git' package is required but not installed. "
        "You can install 'git' package with the command:\n\n"
        "pip install gitpython\n"
    )
    raise RuntimeError(msg)


####################
#     requests     #
####################


@lru_cache
def is_requests_available() -> bool:
    r"""Indicate if the ``requests`` package is installed or not.

    Returns:
        ``True`` if ``requests`` is available otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.imports import is_requests_available
    >>> is_requests_available()

    ```
    """
    return is_package_available("requests")


def check_requests() -> None:
    r"""Check if the ``requests`` package is installed.

    Raises:
        RuntimeError: if the ``requests`` package is not installed.

    Example usage:

    ```pycon

    >>> from feu.imports import check_requests
    >>> check_requests()

    ```
    """
    if not is_requests_available():
        raise_error_requests_missing()


def raise_error_requests_missing() -> NoReturn:
    r"""Raise a RuntimeError to indicate the ``requests`` package is
    missing."""
    msg = (
        "'requests' package is required but not installed. "
        "You can install 'requests' package with the command:\n\n"
        "pip install requests\n"
    )
    raise RuntimeError(msg)


###################
#     urllib3     #
###################


@lru_cache
def is_urllib3_available() -> bool:
    r"""Indicate if the ``urllib3`` package is installed or not.

    Returns:
        ``True`` if ``urllib3`` is available otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.imports import is_urllib3_available
    >>> is_urllib3_available()

    ```
    """
    return is_package_available("urllib3")


def check_urllib3() -> None:
    r"""Check if the ``urllib3`` package is installed.

    Raises:
        RuntimeError: if the ``urllib3`` package is not installed.

    Example usage:

    ```pycon

    >>> from feu.imports import check_urllib3
    >>> check_urllib3()

    ```
    """
    if not is_urllib3_available():
        raise_error_urllib3_missing()


def raise_error_urllib3_missing() -> NoReturn:
    r"""Raise a RuntimeError to indicate the ``urllib3`` package is
    missing."""
    msg = (
        "'urllib3' package is required but not installed. "
        "You can install 'urllib3' package with the command:\n\n"
        "pip install urllib3\n"
    )
    raise RuntimeError(msg)
