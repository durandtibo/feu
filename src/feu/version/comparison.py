r"""Contain functions to compare package versions."""

from __future__ import annotations

__all__ = ["compare_version", "sort_versions"]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.version.runtime import get_package_version

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


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


def sort_versions(versions: Sequence[str], reverse: bool = False) -> list[str]:
    """Sort a list of version strings in ascending or descending order.

    Args:
        versions: A list of version strings.
        reverse: If ``False``, sort in ascending order; if ``True``,
            sort in descending order.

    Returns:
        A new list of version strings sorted according to semantic
            version order.

    Example usage:

    ```pycon

    >>> import operator
    >>> from feu.version import sort_versions
    >>> sort_versions(["1.0.0", "1.2.0", "1.1.0"])
    ['1.0.0', '1.1.0', '1.2.0']
    >>> sort_versions(["1.0.0", "1.2.0", "1.1.0"], reverse=True)
    ['1.2.0', '1.1.0', '1.0.0']

    ```
    """
    return sorted(versions, key=Version, reverse=reverse)
