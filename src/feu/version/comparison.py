r"""Contain functions to compare package versions."""

from __future__ import annotations

__all__ = ["compare_version", "latest_version", "sort_versions"]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.version.runtime import get_package_version

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def compare_version(package: str, op: Callable, version: str) -> bool:
    r"""Compare a package version to a given version.

    Args:
        package: The package to check.
        op: The comparison operator.
        version: The version to compare with.

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


def latest_version(versions: Sequence[str]) -> str:
    """Return the latest version string in a list of version
    identifiers.

    This function compares version strings according to the PEP 440
    specification using :class:`packaging.version.Version`. It supports
    standard releases, pre-releases (alpha, beta, release candidates),
    development releases, post releases, and epoch-based versions.

    Args:
        versions: A list of version strings to compare.

    Returns:
        The highest (latest) version in the list based on PEP 440 ordering.

    Raises:
        ValueError: If ``versions`` is empty.

    Example usage:

    ```pycon

    >>> import operator
    >>> from feu.version import latest_version
    >>> latest_version(["1.0.0", "1.0.1rc1", "1.0.1"])
    '1.0.1'
    >>> latest_version(["1.2.0", "2.0.0a1"])
    '2.0.0a1'

    ```
    """
    if not versions:
        msg = "versions list must not be empty"
        raise ValueError(msg)
    return str(max(Version(v) for v in versions))


def sort_versions(versions: Sequence[str], reverse: bool = False) -> list[str]:
    r"""Sort a list of version strings in ascending or descending order.

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
