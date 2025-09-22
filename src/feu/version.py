r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = [
    "compare_version",
    "filter_stable_versions",
    "filter_valid_versions",
    "get_package_version",
]

from contextlib import suppress
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from packaging.version import InvalidVersion, Version

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
    >>> from feu import compare_version
    >>> compare_version("pytest", op=operator.ge, version="7.3.0")
    True

    ```
    """
    pkg_version = get_package_version(package)
    if pkg_version is None:
        return False
    return op(pkg_version, Version(version))


def get_package_version(package: str) -> Version | None:
    r"""Get the package version.

    Args:
        package: Specifies the package name.

    Returns:
        The package version.

    Example usage:

    ```pycon

    >>> from feu import get_package_version
    >>> get_package_version("pytest")
    <Version('...')>

    ```
    """
    try:
        return Version(version(package))
    except PackageNotFoundError:
        return None


def filter_stable_versions(versions: Sequence[str]) -> list[str]:
    """Filter out pre-release, post-release, and dev-release versions
    from a list of version strings.

    A stable version is defined as:
      - Not a pre-release (e.g., alpha `a`, beta `b`, release candidate `rc`)
      - Not a post-release (e.g., `1.0.0.post1`)
      - Not a development release (e.g., `1.0.0.dev1`)

    Args:
        versions: A list of version strings.

    Returns:
        A list containing only stable version strings.

    Example usage:

    ```pycon

    >>> from feu.version import filter_stable_versions
    >>> versions = filter_stable_versions(
    ...     ["1.0.0", "1.0.0a1", "2.0.0", "2.0.0.dev1", "3.0.0.post1"]
    ... )
    >>> versions
    ['1.0.0', '2.0.0']

    ```
    """
    stable_versions = []
    for v in versions:
        parsed = Version(v)
        if not (parsed.is_prerelease or parsed.is_postrelease or parsed.is_devrelease):
            stable_versions.append(v)
    return stable_versions


def filter_valid_versions(versions: Sequence[str]) -> list[str]:
    """Filter out invalid version strings based on PEP 440.

    A valid version is one that can be parsed by `packaging.version.Version`.
    Invalid versions include strings that don't conform to semantic versioning rules.

    Args:
        versions: A list of version strings.

    Returns:
        A list containing only valid version strings.

    Example usage:

    ```pycon

    >>> from feu.version import filter_valid_versions
    >>> versions = filter_valid_versions(
    ...     [
    ...         "1.0.0",
    ...         "1.0.0a1",
    ...         "2.0.0.post1",
    ...         "not-a-version",
    ...         "",
    ...         "2",
    ...         "3.0",
    ...         "v1.0.0",
    ...         "1.0.0.0.0",
    ...         "4.0.0.dev1",
    ...     ]
    ... )
    >>> versions
    ['1.0.0', '1.0.0a1', '2.0.0.post1', '2', '3.0', 'v1.0.0', '1.0.0.0.0', '4.0.0.dev1']

    ```
    """
    valid_versions = []
    for v in versions:
        with suppress(InvalidVersion):
            Version(v)
            valid_versions.append(v)
    return valid_versions
