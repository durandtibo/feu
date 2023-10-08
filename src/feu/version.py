from __future__ import annotations

__all__ = ["compare_version", "get_package_version"]

from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version

from packaging.version import Version


def compare_version(package: str, op: Callable, version: str) -> bool:
    r"""Compares a package version to a given version.

    Args:
    ----
        package (str): Specifies the package to check.
        op (``Callable``): Specifies the comparison operator.
        version (str): Specifies the version to compare with.

    Returns:
    -------
        bool: The comparison status.

    Example usage:

    .. code-block:: pycon

        >>> import operator
        >>> from feu import compare_version
        >>> compare_version("pytest", op=operator.ge, version="7.3.0")
        True
    """
    pkg_version = get_package_version(package)
    if pkg_version is None:
        return False
    return op(pkg_version, Version(version))


def get_package_version(package: str) -> Version | None:
    r"""Gets the package version.

    Args:
    ----
        package (str): Specifies the package name.

    Returns:
    -------
        ``packaging.version.Version``: The package version.

    Example usage:

    .. code-block:: pycon

        >>> from feu import get_package_version
        >>> get_package_version("pytest")
        <Version('...')>
    """
    try:
        return Version(version(package))
    except PackageNotFoundError:
        return None
