r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = [
    "fetch_latest_major_versions",
    "fetch_latest_minor_versions",
    "fetch_latest_stable_version",
    "fetch_latest_version",
    "fetch_versions",
]


from feu.version.comparison import latest_version, sort_versions
from feu.version.filtering import (
    filter_range_versions,
    filter_stable_versions,
    filter_valid_versions,
    latest_major_versions,
    latest_minor_versions,
    unique_versions,
)
from feu.version.pypi import fetch_pypi_versions


def fetch_versions(
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

    >>> from feu.version import fetch_versions
    >>> versions = fetch_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = fetch_pypi_versions(package)
    versions = filter_valid_versions(versions)
    versions = filter_stable_versions(versions)
    versions = filter_range_versions(versions, lower=lower, upper=upper)
    versions = unique_versions(versions)
    versions = sort_versions(versions)
    return tuple(versions)


def fetch_latest_major_versions(
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

    >>> from feu.version import fetch_latest_major_versions
    >>> versions = fetch_latest_major_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = fetch_versions(package, lower=lower, upper=upper)
    return tuple(latest_major_versions(versions))


def fetch_latest_minor_versions(
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

    >>> from feu.version import fetch_latest_minor_versions
    >>> versions = fetch_latest_minor_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = fetch_versions(package, lower=lower, upper=upper)
    return tuple(latest_minor_versions(versions))


def fetch_latest_version(package: str) -> str:
    r"""Get the latest valid versions for a given package.

    Args:
        package: The package name.

    Returns:
        The latest valid versions.

    Example usage:

    ```pycon

    >>> from feu.version import fetch_latest_version
    >>> version = fetch_latest_version("requests")  # doctest: +SKIP

    ```
    """
    versions = fetch_pypi_versions(package)
    versions = filter_valid_versions(versions)
    return latest_version(versions)


def fetch_latest_stable_version(package: str) -> str:
    r"""Get the latest stable valid versions for a given package.

    Args:
        package: The package name.

    Returns:
        The latest stable valid versions.

    Example usage:

    ```pycon

    >>> from feu.version import fetch_latest_stable_version
    >>> version = fetch_latest_stable_version("requests")  # doctest: +SKIP

    ```
    """
    versions = fetch_pypi_versions(package)
    versions = filter_valid_versions(versions)
    versions = filter_stable_versions(versions)
    return latest_version(versions)
