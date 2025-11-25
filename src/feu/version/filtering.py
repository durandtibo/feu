r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = [
    "filter_every_n_versions",
    "filter_last_n_versions",
    "filter_range_versions",
    "filter_stable_versions",
    "filter_valid_versions",
    "latest_major_versions",
    "latest_minor_versions",
    "unique_versions",
]

from contextlib import suppress
from typing import TYPE_CHECKING

from packaging.version import InvalidVersion, Version

if TYPE_CHECKING:
    from collections.abc import Sequence


def filter_every_n_versions(versions: Sequence[str], n: int) -> list[str]:
    r"""Filter a list of version strings, keeping only every n-th version
    using **0-based indexing**.

    This function preserves the original order of the input list and returns
    a new list containing only the versions at positions that are multiples of
    ``n`` (using 0-based indexing). For example, if ``n = 2``, the function keeps
    the 0th, 2nd, 4th, ... versions from the list.

    Args:
        versions: A list of version strings.
        n: The interval for selecting versions. Must be >= 1.

    Returns:
        A new list containing only every n-th version in ``versions``,
            starting from index 0.

    Raises:
        ValueError: If ``n`` is less than 1.

    Example usage:

    ```pycon

    >>> from feu.version import filter_every_n_versions
    >>> versions = filter_every_n_versions(["1.0", "1.1", "1.2", "1.3", "1.5", "1.6"], n=2)
    >>> versions
    ['1.0', '1.2', '1.5']
    >>> versions = filter_every_n_versions(["1.0", "1.1", "1.2", "1.3", "1.5", "1.6"], n=1)
    >>> versions
    ['1.0', '1.1', '1.2', '1.3', '1.5', '1.6']

    ```
    """
    if n < 1:
        msg = f"n must be >= 1 but received {n}"
        raise ValueError(msg)
    return [v for i, v in enumerate(versions) if i % n == 0]


def filter_last_n_versions(versions: Sequence[str], n: int) -> list[str]:
    r"""Return only the last n versions from a list of version strings.

    This function preserves the original ordering of the final n elements.
    If ``n`` is greater than the number of versions available, the entire list
    is returned. If ``n`` is zero, an empty list is returned.

    Args:
        versions: A list of version strings.
        n: Number of versions to keep from the end of the list. Must be >= 0.

    Returns:
        A new list containing only the last n versions, in order.

    Raises:
        ValueError: If ``n`` is less than 1.

    Example usage:

    ```pycon

    >>> from feu.version import filter_last_n_versions
    >>> versions = filter_last_n_versions(["1.0", "1.1", "1.2", "1.3"], n=2)
    >>> versions
    ['1.2', '1.3']
    >>> versions = filter_last_n_versions(["1.0", "1.1", "1.2", "1.3"], n=5)
    >>> versions
    ['1.0', '1.1', '1.2', '1.3']

    ```
    """
    if n <= 0:
        msg = f"n must be > 0 but received {n}"
        raise ValueError(msg)
    return list(versions[-n:])


def filter_range_versions(
    versions: Sequence[str], lower: str | None = None, upper: str | None = None
) -> list[str]:
    r"""Filter a list of version strings to include only versions within
    optional bounds.

    Args:
        versions: A list of version strings.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If None, no upper limit is applied.

    Returns:
        A list of version strings that fall within the specified bounds.

    Example usage:

    ```pycon

    >>> from feu.version import filter_range_versions
    >>> versions = filter_range_versions(
    ...     ["1.0.0", "1.2.0", "1.3.0", "2.0.0"], lower="1.1.0", upper="2.0.0"
    ... )
    >>> versions
    ['1.2.0', '1.3.0']
    >>> versions = filter_range_versions(["0.9.0", "1.0.0", "1.1.0"], lower="1.0.0")
    >>> versions
    ['1.0.0', '1.1.0']

    ```
    """
    lower_v = Version(lower) if lower else None
    upper_v = Version(upper) if upper else None

    result = []
    for v_str in versions:
        v = Version(v_str)
        if (lower_v is None or v >= lower_v) and (upper_v is None or v < upper_v):
            result.append(v_str)
    return result


def filter_stable_versions(versions: Sequence[str]) -> list[str]:
    r"""Filter out pre-release, post-release, and dev-release versions
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
    r"""Filter out invalid version strings based on PEP 440.

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


def latest_major_versions(versions: Sequence[str]) -> list[str]:
    r"""Return the latest version for each major version in a list of
    semantic versions.

    This function takes a list of semantic version strings
    (e.g. "1.0.0", "1.2.1", "2.0.0"), groups them by their major
    version number, and returns only the latest version from
    each major group (based on minor and patch numbers).

    Args:
        versions: A list of version strings in semantic version format.

    Returns:
        A list containing the latest version for each major version,
            sorted by major version number.

    Example usage:

    ```pycon

    >>> from feu.version import latest_major_versions
    >>> versions = latest_major_versions(["1.0.0", "1.1.0", "1.2.0", "1.2.1", "2.0.0"])
    >>> versions
    ['1.2.1', '2.0.0']

    ```
    """
    by_major = {}
    for v_str in versions:
        v = Version(v_str)
        current = by_major.get(v.major)
        if current is None or v > current:
            by_major[v.major] = v
    return [str(by_major[k]) for k in sorted(by_major)]


def latest_minor_versions(versions: Sequence[str]) -> list[str]:
    r"""Return the latest version for each minor version in a list of
    semantic versions.

    This function takes a list of semantic version strings
    (e.g. "1.0.0", "1.0.1", "1.1.0", "2.0.0"), groups them by their
    major and minor version numbers, and returns only the latest
    version from each minor group (based on the patch number).

    Args:
        versions: A list of version strings in semantic version format.

    Returns:
        A list containing the latest version for each minor version,
            sorted by major and minor version numbers.

    Example usage:

    ```pycon

    >>> from feu.version import latest_major_versions
    >>> versions = latest_minor_versions(["1.0.0", "1.0.1", "1.1.0", "1.1.2", "2.0.0", "2.0.3"])
    >>> versions
    ['1.0.1', '1.1.2', '2.0.3']

    ```
    """
    by_minor = {}
    for v_str in versions:
        v = Version(v_str)
        key = (v.major, v.minor)
        current = by_minor.get(key)
        if current is None or v > current:
            by_minor[key] = v
    return [str(by_minor[k]) for k in sorted(by_minor)]


def unique_versions(versions: Sequence[str]) -> list[str]:
    r"""Return a list of unique versions while preserving order.

    Args:
        versions: A list of version strings.

    Returns:
        A list containing only unique version strings, preserving the
            original order of first occurrence.

    Example usage:

    ```pycon

    >>> from feu.version import unique_versions, sort_versions
    >>> versions = sort_versions(unique_versions(["1.0.0", "1.0.1", "1.0.0", "1.2.0"]))
    >>> versions
    ['1.0.0', '1.0.1', '1.2.0']

    ```
    """
    return list(set(versions))
