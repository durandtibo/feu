r"""Contain functions to compare package versions."""

from __future__ import annotations

__all__ = ["compare_version"]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.version.runtime import get_package_version

if TYPE_CHECKING:
    from collections.abc import Callable


def compare_version(package: str, op: Callable, version: str) -> bool:
    r"""Compare a package version to a given version.

    Args:
        package: Specifies the package to check.
        op: Specifies the comparison operator.
        version: Specifies the version to compare with.

    Returns:
        The comparison status.

    Example usage:

    ```pycon

    >>> import operator
    >>> from feu.version import compare_version
    >>> compare_version("pytest", op=operator.ge, version="7.3.0")
    True

    ```
    """
    pkg_version = get_package_version(package)
    if pkg_version is None:
        return False
    return op(pkg_version, Version(version))
