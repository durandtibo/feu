r"""Contain functions to fetch the versions of a package published on
PyPI."""

from __future__ import annotations

__all__ = [
    "fetch_latest_major_versions_map",
    "fetch_latest_minor_versions_map",
    "fetch_latest_stable_version",
    "fetch_latest_version",
    "fetch_latest_versions",
    "fetch_package_versions",
    "fetch_versions",
]

from typing import TYPE_CHECKING, Literal

from packaging.utils import canonicalize_name

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
from feu.version.pyproject import read_pyproject_bounds

if TYPE_CHECKING:
    from collections.abc import Collection, Sequence
    from pathlib import Path

    from feu.version.bound import PackageBounds


def fetch_versions(
    package: str, *, lower: str | None = None, upper: str | None = None
) -> tuple[str, ...]:
    r"""Get the valid stable versions for a given package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If ``None``, no upper limit is applied.

    Returns:
        A tuple containing the unique, valid, stable versions in
            ascending order.

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


def fetch_latest_versions(
    package: str,
    *,
    group: Literal["major", "minor"],
    lower: str | None = None,
    upper: str | None = None,
    include_lower_bound: bool = False,
) -> tuple[str, ...]:
    r"""Get the latest version of each major (or minor) version of a
    package.

    Args:
        package: The package name.
        group: ``"major"`` to get the latest version of each major
            version, ``"minor"`` for each ``major.minor`` version.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If ``None``, no upper limit is applied.
        include_lower_bound: If ``True`` and ``lower`` is not ``None``,
            the first stable version at or above ``lower`` is included
            in the result. This ensures the lower bound itself is always
            represented, even if it is not the latest patch of its
            group. If ``lower`` is ``None``, this argument has no
            effect.

    Returns:
        A tuple containing the latest version of each group, in
            ascending order. If ``include_lower_bound`` is ``True`` and
            ``lower`` is not ``None``, the first stable version at or
            above ``lower`` is also included.

    Raises:
        ValueError: If ``group`` is not ``"major"`` or ``"minor"``.

    Example:
        ```pycon
        >>> from feu.version import fetch_latest_versions
        >>> versions = fetch_latest_versions(
        ...     "requests", group="minor", lower="2.28"
        ... )  # doctest: +SKIP

        ```
    """
    if group not in ("major", "minor"):
        msg = f"group must be 'major' or 'minor' but received {group!r}"
        raise ValueError(msg)
    versions = fetch_versions(package, lower=lower, upper=upper)
    latest = latest_major_versions if group == "major" else latest_minor_versions
    result = list(latest(versions))
    if include_lower_bound and lower is not None and versions:
        result = unique_versions([versions[0], *result])
    return tuple(sort_versions(result))


def fetch_latest_version(package: str) -> str:
    r"""Get the latest valid version for a given package.

    The latest version can be a pre-release, post-release or
    development release.

    Args:
        package: The package name.

    Returns:
        The latest valid version.

    Raises:
        ValueError: If the package has no valid version.

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
    r"""Get the latest stable valid version for a given package.

    Args:
        package: The package name.

    Returns:
        The latest stable valid version.

    Raises:
        ValueError: If the package has no stable valid version.

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


def _fetch_versions_map(
    packages: Sequence[PackageBounds],
    group: Literal["major", "minor"],
    *,
    include_lower_bound: bool,
) -> dict[str, list[str]]:
    r"""Fetch the latest major or minor versions of several packages.

    Args:
        packages: The bounds of the packages. If a package appears
            more than once, the last entry wins.
        group: ``"major"`` or ``"minor"``.
        include_lower_bound: See ``fetch_latest_versions``.

    Returns:
        A dictionary mapping each package name to its versions.
    """
    return {
        bounds.name: list(
            fetch_latest_versions(
                bounds.name,
                group=group,
                lower=bounds.lower,
                include_lower_bound=include_lower_bound,
            )
        )
        for bounds in packages
    }


def fetch_latest_major_versions_map(
    packages: Sequence[PackageBounds], *, include_lower_bound: bool = False
) -> dict[str, list[str]]:
    r"""Fetch the latest major versions for a sequence of packages.

    This function is kept for the scripts that copy
    ``dev/generate_versions.py``; use ``fetch_package_versions`` in new
    code.

    Args:
        packages: A sequence of ``PackageBounds`` instances, typically
            obtained from ``read_pyproject_bounds``. If a package
            appears more than once in ``packages`` (e.g. because it
            was found in multiple sections), the last entry wins.
        include_lower_bound: If ``True``, the first stable version at or
            above each package's lower bound is included in its version
            list. Has no effect for packages whose lower bound is
            ``None``.

    Returns:
        A dictionary mapping each package name to the list of latest major
            version strings returned by ``fetch_latest_versions``.

    Example:
        ```pycon
        >>> from feu.version import PackageBounds, fetch_latest_major_versions_map
        >>> bounds = [PackageBounds("requests", "2.28", None, "project.dependencies")]
        >>> versions = fetch_latest_major_versions_map(
        ...     bounds, include_lower_bound=True
        ... )  # doctest: +SKIP

        ```
    """
    return _fetch_versions_map(packages, "major", include_lower_bound=include_lower_bound)


def fetch_latest_minor_versions_map(
    packages: Sequence[PackageBounds], *, include_lower_bound: bool = False
) -> dict[str, list[str]]:
    r"""Fetch the latest minor versions for a sequence of packages.

    This function is kept for the scripts that copy
    ``dev/generate_versions.py``; use ``fetch_package_versions`` in new
    code.

    Args:
        packages: A sequence of ``PackageBounds`` instances, typically
            obtained from ``read_pyproject_bounds``. If a package
            appears more than once in ``packages`` (e.g. because it
            was found in multiple sections), the last entry wins.
        include_lower_bound: If ``True``, the first stable version at or
            above each package's lower bound is included in its version
            list. Has no effect for packages whose lower bound is
            ``None``.

    Returns:
        A dictionary mapping each package name to the list of latest minor
            version strings returned by ``fetch_latest_versions``.

    Example:
        ```pycon
        >>> from feu.version import PackageBounds, fetch_latest_minor_versions_map
        >>> bounds = [PackageBounds("requests", "2.28", None, "project.dependencies")]
        >>> versions = fetch_latest_minor_versions_map(
        ...     bounds, include_lower_bound=True
        ... )  # doctest: +SKIP

        ```
    """
    return _fetch_versions_map(packages, "minor", include_lower_bound=include_lower_bound)


def fetch_package_versions(
    pyproject: str | Path,
    *,
    major_only: Collection[str] = ("packaging",),
    include_lower_bound: bool = True,
) -> dict[str, list[str]]:
    r"""Fetch the versions to test of the dependencies of a project.

    The dependencies are read from ``[project.dependencies]`` and
    ``[project.optional-dependencies.*]`` of the ``pyproject.toml``
    file (not from the ``[dependency-groups.*]``). For each package,
    the latest version of each minor version at or above the lower
    bound is returned, or the latest version of each major version for
    the packages of ``major_only``.

    Args:
        pyproject: Path to the ``pyproject.toml`` file.
        major_only: The packages for which only the latest version of
            each major version is returned. The names are compared in
            their canonical form.
        include_lower_bound: If ``True``, the first stable version at or
            above the lower bound of each package is included.

    Returns:
        A dictionary mapping each canonical package name to its
            versions, sorted by package name. If a package appears
            more than once, the last entry wins.

    Raises:
        FileNotFoundError: If the file does not exist.
        tomllib.TOMLDecodeError: If the file is not valid TOML.

    Example:
        ```pycon
        >>> from feu.version import fetch_package_versions
        >>> versions = fetch_package_versions("pyproject.toml")  # doctest: +SKIP

        ```
    """
    majors = {canonicalize_name(name) for name in major_only}
    bounds = [b for b in read_pyproject_bounds(pyproject) if b.section.startswith("project.")]
    result = _fetch_versions_map(
        [b for b in bounds if b.name in majors], "major", include_lower_bound=include_lower_bound
    ) | _fetch_versions_map(
        [b for b in bounds if b.name not in majors],
        "minor",
        include_lower_bound=include_lower_bound,
    )
    return dict(sorted(result.items()))
