r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = ["get_latest_major_versions", "get_latest_minor_versions", "get_versions"]


from feu.version.comparison import sort_versions
from feu.version.filtering import (
    filter_range_versions,
    filter_stable_versions,
    filter_valid_versions,
    latest_major_versions,
    latest_minor_versions,
    unique_versions,
)
from feu.version.pypi import get_pypi_versions


def get_versions(
    package: str, lower: str | None = None, upper: str | None = None
) -> tuple[str, ...]:
    r"""Get the valid versions for a given package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If None, no upper limit is applied.

    Returns:
        A tuple containing the valid versions.

    Example usage:

    ```pycon

    >>> from feu.version import get_versions
    >>> versions = get_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = get_pypi_versions(package)
    versions = filter_valid_versions(versions)
    versions = filter_stable_versions(versions)
    versions = filter_range_versions(versions, lower=lower, upper=upper)
    versions = unique_versions(versions)
    versions = sort_versions(versions)
    return tuple(versions)


def get_latest_major_versions(
    package: str, lower: str | None = None, upper: str | None = None
) -> tuple[str, ...]:
    r"""Get the latest version for each major version for a given
    package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If None, no upper limit is applied.

    Returns:
        A tuple containing the latest version for each major version,
            sorted by major version number.

    Example usage:

    ```pycon

    >>> from feu.version import get_latest_major_versions
    >>> versions = get_latest_major_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = get_versions(package, lower=lower, upper=upper)
    return tuple(latest_major_versions(versions))


def get_latest_minor_versions(
    package: str, lower: str | None = None, upper: str | None = None
) -> tuple[str, ...]:
    r"""Get the latest version for each minor version for a given
    package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If None, no upper limit is applied.

    Returns:
        A tuple containing the latest version for each minor version,
            sorted by minor version number.

    Example usage:

    ```pycon

    >>> from feu.version import get_latest_minor_versions
    >>> versions = get_latest_minor_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = get_versions(package, lower=lower, upper=upper)
    return tuple(latest_minor_versions(versions))
