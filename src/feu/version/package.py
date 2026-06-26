r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = [
    "fetch_latest_major_versions",
    "fetch_latest_major_versions_map",
    "fetch_latest_minor_versions",
    "fetch_latest_minor_versions_map",
    "fetch_latest_stable_version",
    "fetch_latest_version",
    "fetch_sampled_latest_minor_versions",
    "fetch_versions",
]


from typing import TYPE_CHECKING

from feu.version.comparison import latest_version, sort_versions
from feu.version.filtering import (
    filter_every_n_versions,
    filter_last_n_versions,
    filter_range_versions,
    filter_stable_versions,
    filter_valid_versions,
    latest_major_versions,
    latest_minor_versions,
    unique_versions,
)
from feu.version.pypi import fetch_pypi_versions

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.version import PackageBounds


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

    Example:
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
    package: str,
    lower: str | None = None,
    upper: str | None = None,
    include_lower_bound: bool = False,
) -> tuple[str, ...]:
    r"""Get the latest version for each major version for a given
    package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If ``None``, no upper limit is applied.
        include_lower_bound: If ``True`` and ``lower`` is not ``None``,
            the first stable version at or above ``lower`` is included
            in the result. This ensures the lower bound itself is always
            represented, even if it is not the latest patch for its
            major release. If ``lower`` is ``None``, this argument has
            no effect. Defaults to ``False``.

    Returns:
        A tuple containing the latest version for each major version,
            sorted by major version number. If ``include_lower_bound`` is
            ``True`` and ``lower`` is not ``None``, the first stable version
            at or above ``lower`` is also included.

    Example:
        ```pycon
        >>> from feu.version import fetch_latest_major_versions
        >>> versions = fetch_latest_major_versions("requests", lower="2.0")  # doctest: +SKIP

        ```
    """
    versions = fetch_versions(package, lower=lower, upper=upper)
    result = list(latest_major_versions(versions))
    if include_lower_bound and versions:
        result = unique_versions([versions[0], *result])
    return tuple(sort_versions(result))


def fetch_latest_minor_versions(
    package: str,
    lower: str | None = None,
    upper: str | None = None,
    include_lower_bound: bool = False,
) -> tuple[str, ...]:
    r"""Get the latest version for each minor version for a given
    package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If ``None``, no upper limit is applied.
        include_lower_bound: If ``True`` and ``lower`` is not ``None``,
            the first stable version at or above ``lower`` is included
            in the result. This ensures the lower bound itself is always
            represented, even if it is not the latest patch for its
            minor release. If ``lower`` is ``None``, this argument has
            no effect. Defaults to ``False``.

    Returns:
        A tuple containing the latest version for each minor version,
            sorted by minor version number. If ``include_lower_bound`` is
            ``True`` and ``lower`` is not ``None``, the first stable version
            at or above ``lower`` is also included.

    Example:
        ```pycon
        >>> from feu.version import fetch_latest_minor_versions
        >>> versions = fetch_latest_minor_versions("requests", lower="2.28")  # doctest: +SKIP

        ```
    """
    versions = fetch_versions(package, lower=lower, upper=upper)
    result = list(latest_minor_versions(versions))
    if include_lower_bound and versions:
        result = unique_versions([versions[0], *result])
    return tuple(sort_versions(result))


def fetch_sampled_latest_minor_versions(
    package: str,
    lower: str | None = None,
    upper: str | None = None,
    n: int = 1,
    include_lower_bound: bool = False,
) -> tuple[str, ...]:
    r"""Get a sampled subset of the latest minor versions for a given
    package.

    Fetches the latest version for each minor release, then returns every
    ``n``-th version plus the most recent one, deduplicated and sorted.
    This is useful for generating a representative but not exhaustive set
    of versions to test against.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If ``None``, no upper limit is applied.
        n: The sampling stride. Every ``n``-th version is kept, along
            with the most recent version. Defaults to ``1``, which
            keeps all versions.
        include_lower_bound: If ``True`` and ``lower`` is not ``None``,
            the first stable version at or above ``lower`` is included
            in the result alongside the sampled versions. Has no effect
            if ``lower`` is ``None``. Defaults to ``False``.

    Returns:
        A sorted tuple of sampled version strings.

    Example:
        ```pycon
        >>> from feu.version import fetch_sampled_latest_minor_versions
        >>> versions = fetch_sampled_latest_minor_versions(
        ...     "requests", lower="2.28", n=2
        ... )  # doctest: +SKIP

        ```
    """
    versions = fetch_latest_minor_versions(package=package, lower=lower, upper=upper)
    sampled = filter_every_n_versions(versions, n=n) + filter_last_n_versions(versions, n=1)
    if include_lower_bound and lower is not None and versions:
        sampled = [*sampled, versions[0]]
    return tuple(sort_versions(unique_versions(sampled)))


def fetch_latest_version(package: str) -> str:
    r"""Get the latest valid versions for a given package.

    Args:
        package: The package name.

    Returns:
        The latest valid versions.

    Example:
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

    Example:
        ```pycon
        >>> from feu.version import fetch_latest_stable_version
        >>> version = fetch_latest_stable_version("requests")  # doctest: +SKIP

        ```
    """
    versions = fetch_pypi_versions(package)
    versions = filter_valid_versions(versions)
    versions = filter_stable_versions(versions)
    return latest_version(versions)


def fetch_latest_major_versions_map(
    packages: Sequence[PackageBounds],
    include_lower_bound: bool = False,
) -> dict[str, list[str]]:
    """Fetch the latest major versions for a sequence of packages.

    For each ``PackageBounds`` in ``packages``, calls
    ``fetch_latest_major_versions`` with the package name and lower bound,
    and collects the results into a dictionary.

    If a package appears more than once in ``packages`` (e.g. because it
    was found in multiple sections), the last entry wins.

    Args:
        packages: A sequence of ``PackageBounds`` instances, typically
            obtained from ``read_pyproject_dependencies`` or
            ``read_pyproject_optional_dependencies``.
        include_lower_bound: If ``True``, the first stable version at or
            above each package's lower bound is included in its version
            list. Has no effect for packages whose lower bound is
            ``None``. Defaults to ``False``.

    Returns:
        A dictionary mapping each package name to the list of latest major
            version strings returned by ``fetch_latest_major_versions``.

    Example:
        ```pycon
        >>> from feu.version import fetch_latest_major_versions_map, read_pyproject_dependencies
        >>> bounds = read_pyproject_dependencies("pyproject.toml")  # doctest: +SKIP
        >>> versions = fetch_latest_major_versions_map(bounds)  # doctest: +SKIP

        ```
    """
    return {
        bounds.name: list(
            fetch_latest_major_versions(
                bounds.name, lower=bounds.lower, include_lower_bound=include_lower_bound
            )
        )
        for bounds in packages
    }


def fetch_latest_minor_versions_map(
    packages: Sequence[PackageBounds],
    include_lower_bound: bool = False,
) -> dict[str, list[str]]:
    """Fetch the latest minor versions for a sequence of packages.

    For each ``PackageBounds`` in ``packages``, calls
    ``fetch_latest_minor_versions`` with the package name and lower bound,
    and collects the results into a dictionary.

    If a package appears more than once in ``packages`` (e.g. because it
    was found in multiple sections), the last entry wins.

    Args:
        packages: A sequence of ``PackageBounds`` instances, typically
            obtained from ``read_pyproject_dependencies`` or
            ``read_pyproject_optional_dependencies``.
        include_lower_bound: If ``True``, the first stable version at or
            above each package's lower bound is included in its version
            list. Has no effect for packages whose lower bound is
            ``None``. Defaults to ``False``.

    Returns:
        A dictionary mapping each package name to the list of latest minor
            version strings returned by ``fetch_latest_minor_versions``.

    Example:
        ```pycon
        >>> from feu.version import fetch_latest_minor_versions_map, read_pyproject_dependencies
        >>> bounds = read_pyproject_dependencies("pyproject.toml")  # doctest: +SKIP
        >>> versions = fetch_latest_minor_versions_map(bounds)  # doctest: +SKIP
        >>> versions_with_lower = fetch_latest_minor_versions_map(
        ...     bounds, include_lower_bound=True
        ... )  # doctest: +SKIP

        ```
    """
    return {
        bounds.name: list(
            fetch_latest_minor_versions(
                bounds.name, lower=bounds.lower, include_lower_bound=include_lower_bound
            )
        )
        for bounds in packages
    }
