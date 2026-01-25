r"""Contain functions to check if a package or module is available."""

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
    "raise_package_missing_error",
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

    Example:
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
    # AttributeError is included for defensive programming, though it's not a documented
    # exception from find_spec and may indicate a real bug if raised
    with suppress(ModuleNotFoundError, ImportError, AttributeError):
        return find_spec(package) is not None
    return False


@lru_cache
def is_module_available(module: str) -> bool:
    r"""Check if a module path is available.

    Args:
        module: The module to check.

    Returns:
        ``True`` if the module is available, otherwise ``False``.

    Example:
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


def raise_package_missing_error(package_name: str, install_cmd: str) -> NoReturn:
    r"""Raise a RuntimeError for a missing package.

    Args:
        package_name: The name of the missing package.
        install_cmd: The pip install command for the package.

    Raises:
        RuntimeError: Always raised to indicate the package is missing.
    """
    msg = (
        f"'{package_name}' package is required but not installed. "
        f"You can install '{package_name}' package with the command:\n\n"
        f"pip install {install_cmd}\n"
    )
    raise RuntimeError(msg)


#################
#     click     #
#################


@lru_cache
def is_click_available() -> bool:
    r"""Indicate if the ``click`` package is installed or not.

    Returns:
        ``True`` if ``click`` is available otherwise ``False``.

    Example:
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

    Example:
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
    raise_package_missing_error("click", "click")


###############
#     git     #
###############


@lru_cache
def is_git_available() -> bool:
    r"""Indicate if the ``git`` package is installed or not.

    Returns:
        ``True`` if ``git`` is available otherwise ``False``.

    Example:
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

    Example:
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
    raise_package_missing_error("git", "gitpython")


####################
#     requests     #
####################


@lru_cache
def is_requests_available() -> bool:
    r"""Indicate if the ``requests`` package is installed or not.

    Returns:
        ``True`` if ``requests`` is available otherwise ``False``.

    Example:
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

    Example:
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
    raise_package_missing_error("requests", "requests")


###################
#     urllib3     #
###################


@lru_cache
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
        raise_error_urllib3_missing()


def raise_error_urllib3_missing() -> NoReturn:
    r"""Raise a RuntimeError to indicate the ``urllib3`` package is
    missing."""
    raise_package_missing_error("urllib3", "urllib3")
