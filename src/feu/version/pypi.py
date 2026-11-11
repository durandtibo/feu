r"""Contain functions to fetch package metadata from PyPI.

The metadata of a project is fetched once with the Simple API in its
JSON form (PEP 691 and PEP 700), cached by canonical project name, and
returned as immutable values. Everything else (versions, wheel file
names, ``requires-python``) is derived from it.
"""

from __future__ import annotations

__all__ = [
    "PypiFile",
    "PypiProject",
    "fetch_pypi_pinned_dependency_version",
    "fetch_pypi_project",
    "fetch_pypi_requires_python",
    "fetch_pypi_versions",
    "fetch_pypi_wheel_filenames",
]

from dataclasses import dataclass
from datetime import UTC, date, datetime
from functools import cache
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import (
    InvalidSdistFilename,
    InvalidWheelFilename,
    canonicalize_name,
    parse_sdist_filename,
    parse_wheel_filename,
)
from packaging.version import InvalidVersion, Version

from feu.utils.http import fetch_data

if TYPE_CHECKING:
    from collections.abc import Mapping

_SIMPLE_API_ACCEPT = "application/vnd.pypi.simple.v1+json"


@dataclass(frozen=True)
class PypiFile:
    r"""Represent a file of a release published on PyPI.

    Args:
        filename: The file name, e.g. ``"numpy-2.0.2.tar.gz"``.
        requires_python: The ``requires-python`` specifier of the file
            (e.g. ``">=3.9"``), or ``None``.
        yanked: ``True`` if the file is yanked.
        uploaded: The upload time (UTC), or ``None`` if unknown.
    """

    filename: str
    requires_python: str | None
    yanked: bool
    uploaded: datetime | None


@dataclass(frozen=True)
class PypiProject:
    r"""Represent a project published on PyPI.

    Args:
        name: The canonical project name (PEP 503).
        releases: The files of each release, in PEP 440 ascending order
            of the release versions. The mapping is read-only. A
            release without any recognised file maps to an empty
            tuple.

    Example:
        ```pycon
        >>> from feu.version.pypi import PypiProject
        >>> PypiProject(name="numpy", releases={})
        PypiProject(name='numpy', releases={})

        ```
    """

    name: str
    releases: Mapping[str, tuple[PypiFile, ...]]


def _to_date(value: date | str) -> date:
    r"""Convert a date or ISO-formatted string to a ``date`` object.

    Args:
        value: A ``date`` object or an ISO 8601 formatted string
            e.g. ``'2024-01-01'``.

    Returns:
        The ``date`` object.

    Raises:
        ValueError: If ``value`` is a string that is not a valid ISO
            8601 date.
    """
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _parse_upload_time(value: str | None) -> datetime | None:
    r"""Parse the ``upload-time`` of a file of the Simple API.

    Args:
        value: The ISO 8601 time, e.g. ``"2017-05-03T20:58:46.547771Z"``,
            or ``None``.

    Returns:
        The time, in UTC, or ``None`` if ``value`` is empty.
    """
    if not value:
        return None
    return datetime.fromisoformat(value).astimezone(UTC)


def _file_version(filename: str) -> Version | None:
    r"""Get the version of a release file from its file name.

    Args:
        filename: The wheel or source distribution file name.

    Returns:
        The version, or ``None`` if the file name is not a wheel or a
            source distribution file name (e.g. a legacy ``.egg``).
    """
    try:
        if filename.endswith(".whl"):
            return parse_wheel_filename(filename)[1]
        return parse_sdist_filename(filename)[1]
    except (InvalidWheelFilename, InvalidSdistFilename, InvalidVersion):
        return None


def _parse_project(name: str, document: Mapping[str, Any]) -> PypiProject:
    r"""Build a project from a Simple API document.

    Args:
        name: The canonical project name.
        document: The JSON document of the Simple API (PEP 691 and
            PEP 700).

    Returns:
        The project. The versions that are not PEP 440 versions and the
            files that are neither wheels nor source distributions are
            skipped.
    """
    parsed: dict[Version, str] = {}
    for text in document.get("versions", []):
        try:
            parsed[Version(text)] = text
        except InvalidVersion:
            continue
    files: dict[Version, list[PypiFile]] = {version: [] for version in parsed}
    for entry in document.get("files", []):
        version = _file_version(entry["filename"])
        if version is None:
            continue
        if version not in parsed:
            parsed[version] = str(version)
            files[version] = []
        files[version].append(
            PypiFile(
                filename=entry["filename"],
                requires_python=entry.get("requires-python") or None,
                yanked=bool(entry.get("yanked")),
                uploaded=_parse_upload_time(entry.get("upload-time")),
            )
        )
    releases = {parsed[version]: tuple(files[version]) for version in sorted(parsed)}
    return PypiProject(name=name, releases=MappingProxyType(releases))


@cache
def _fetch_pypi_project(name: str) -> PypiProject:
    r"""Fetch and cache a project by canonical name.

    Args:
        name: The canonical project name.

    Returns:
        The project.
    """
    document = fetch_data(
        url=f"https://pypi.org/simple/{name}/",
        timeout=10,
        headers={"Accept": _SIMPLE_API_ACCEPT},
    )
    return _parse_project(name, document)


def fetch_pypi_project(package: str) -> PypiProject:
    r"""Fetch the metadata of a project from PyPI.

    One request to the Simple API (``https://pypi.org/simple/<name>/``,
    JSON form) gives the versions, the file names, ``requires-python``,
    ``yanked`` and the upload time. The result is cached by canonical
    project name and is immutable.

    Args:
        package: The package name. It is canonicalised (PEP 503).

    Returns:
        The project.

    Raises:
        RuntimeError: If the request fails.
        MissingPackageError: If ``requests`` is not installed.

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_project
        >>> project = fetch_pypi_project("requests")  # doctest: +SKIP
        >>> list(project.releases)[:2]  # doctest: +SKIP
        ['0.0.1', '0.1.0']

        ```
    """
    return _fetch_pypi_project(canonicalize_name(package))


def _is_yanked(files: tuple[PypiFile, ...]) -> bool:
    r"""Indicate if a release is yanked.

    A release is considered yanked if it has at least one file and all
    its files are yanked.

    Args:
        files: The files of a release.

    Returns:
        ``True`` if the release is yanked, otherwise ``False``.
    """
    return bool(files) and all(file.yanked for file in files)


def _release_date(files: tuple[PypiFile, ...]) -> date | None:
    r"""Get the release date (UTC) of a version from its files.

    The release date is the earliest upload date among the files.

    Args:
        files: The files of a release.

    Returns:
        The release date, or ``None`` if no file has an upload time.
    """
    times = [file.uploaded for file in files if file.uploaded is not None]
    return min(times).date() if times else None


def fetch_pypi_versions(
    package: str,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
    ignore_yanked: bool = True,
) -> tuple[str, ...]:
    r"""Get the package versions available on PyPI.

    Args:
        package: The package name.
        start_date: If specified, only the versions released on or
            after this date (UTC) are returned. The date can be a
            ``date`` object or an ISO 8601 formatted string
            e.g. ``'2024-01-01'``.
        end_date: If specified, only the versions released on or
            before this date (UTC) are returned. The date can be a
            ``date`` object or an ISO 8601 formatted string
            e.g. ``'2024-12-31'``.
        ignore_yanked: If ``True``, yanked versions are excluded
            from the returned versions.

    Returns:
        A tuple containing the version strings in ascending PEP 440
            order. Use ``[::-1]`` for the descending order. The
            release date of a version is the earliest upload time of
            its files, so a version without any file is dropped when a
            date bound is given.

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_versions
        >>> versions = fetch_pypi_versions("requests")  # doctest: +SKIP
        >>> versions = fetch_pypi_versions(
        ...     "requests", start_date="2024-01-01", end_date="2024-12-31"
        ... )  # doctest: +SKIP

        ```
    """
    releases = fetch_pypi_project(package).releases
    start = _to_date(start_date) if start_date is not None else None
    end = _to_date(end_date) if end_date is not None else None
    versions = []
    for version, files in releases.items():
        if ignore_yanked and _is_yanked(files):
            continue
        if start is not None or end is not None:
            released = _release_date(files)
            if released is None:
                continue
            if (start is not None and released < start) or (end is not None and released > end):
                continue
        versions.append(version)
    return tuple(versions)


def fetch_pypi_requires_python(package: str) -> Mapping[str, str | None]:
    r"""Get the ``requires-python`` specifier for each release of a
    package on PyPI.

    Args:
        package: The package name.

    Returns:
        A read-only mapping from each release version string to its
            ``requires-python`` specifier (e.g. ``">=3.9"``), or
            ``None`` if the release has no files or no file declares
            one. The first file that declares a specifier is used.

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_requires_python
        >>> mapping = fetch_pypi_requires_python("requests")  # doctest: +SKIP

        ```
    """
    return MappingProxyType(
        {
            version: next((f.requires_python for f in files if f.requires_python), None)
            for version, files in fetch_pypi_project(package).releases.items()
        }
    )


def fetch_pypi_wheel_filenames(package: str) -> Mapping[str, tuple[str, ...]]:
    r"""Get the wheel file names for each release of a package on PyPI.

    Args:
        package: The package name.

    Returns:
        A read-only mapping from each release version string to a
            tuple of its wheel file names (an empty tuple if the
            release has no wheel).

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_wheel_filenames
        >>> mapping = fetch_pypi_wheel_filenames("numpy")  # doctest: +SKIP

        ```
    """
    return MappingProxyType(
        {
            version: tuple(f.filename for f in files if f.filename.endswith(".whl"))
            for version, files in fetch_pypi_project(package).releases.items()
        }
    )


@cache
def fetch_pypi_pinned_dependency_version(package: str, version: str, dependency: str) -> str | None:
    r"""Get the exact pinned version of a dependency required by a
    specific release of a package on PyPI.

    This is only able to detect an exact pin (e.g. ``dependency==1.2.3``).
    It is intended for packages that pin a compiled dependency to an
    exact version per release, e.g. ``pydantic`` pinning
    ``pydantic-core``. The package names are compared in their
    canonical form (PEP 503). A requirement with an environment marker
    (e.g. ``dependency==1.2.3; python_version < "3.9"``) is skipped.
    The result is cached.

    Args:
        package: The package name.
        version: The release version to inspect.
        dependency: The dependency name to look for (e.g.
            ``"pydantic-core"``).

    Returns:
        The exact pinned version of ``dependency`` required by
            ``package==version``, or ``None`` if the release has no
            such exact pin.

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_pinned_dependency_version
        >>> version = fetch_pypi_pinned_dependency_version(
        ...     "pydantic", "2.9.0", "pydantic-core"
        ... )  # doctest: +SKIP

        ```
    """
    name = canonicalize_name(package)
    # This endpoint is not deprecated: only the ``releases`` key of the
    # project document is.
    metadata = fetch_data(url=f"https://pypi.org/pypi/{name}/{version}/json", timeout=10)
    for requirement_str in metadata["info"].get("requires_dist") or []:
        try:
            requirement = Requirement(requirement_str)
        except InvalidRequirement:  # pragma: no cover
            continue
        if requirement.marker is not None:
            continue
        if canonicalize_name(requirement.name) != canonicalize_name(dependency):
            continue
        for specifier in requirement.specifier:
            if specifier.operator == "==":
                return specifier.version
    return None
