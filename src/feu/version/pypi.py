r"""Contain PyPI utility functions."""

from __future__ import annotations

__all__ = ["fetch_pypi_requires_python", "fetch_pypi_versions", "fetch_pypi_wheel_filenames"]

from datetime import date, datetime
from functools import lru_cache

from feu.utils.http import fetch_data


def _to_date(value: date | str) -> date:
    r"""Convert a date or ISO-formatted string to a ``date`` object."""
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _release_date(files: list[dict] | None) -> date | None:
    r"""Get the release date of a version from its list of files.

    The release date is the earliest upload date among the files.
    """
    upload_times = [
        file["upload_time_iso_8601"] for file in (files or []) if file.get("upload_time_iso_8601")
    ]
    if not upload_times:
        return None
    return min(datetime.fromisoformat(t) for t in upload_times).date()


@lru_cache
def fetch_pypi_requires_python(package: str) -> dict[str, str | None]:
    r"""Get the ``requires_python`` specifier for each release of a
    package on PyPI.

    Args:
        package: The package name.

    Returns:
        A dictionary mapping each release version string to its
            ``requires_python`` specifier (e.g. ``">=3.9"``), or
            ``None`` if the release has no files or does not declare
            a ``requires_python`` constraint.

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_requires_python
        >>> mapping = fetch_pypi_requires_python("requests")  # doctest: +SKIP

        ```
    """
    metadata = fetch_data(url=f"https://pypi.org/pypi/{package}/json", timeout=10)
    result: dict[str, str | None] = {}
    for version, files in metadata["releases"].items():
        requires_python = None
        for file in files or []:
            requires_python = file.get("requires_python")
            if requires_python:
                break
        result[version] = requires_python
    return result


@lru_cache
def fetch_pypi_wheel_filenames(package: str) -> dict[str, tuple[str, ...]]:
    r"""Get the wheel filenames for each release of a package on PyPI.

    Args:
        package: The package name.

    Returns:
        A dictionary mapping each release version string to a tuple of
            its ``bdist_wheel`` filenames (empty tuple if the release
            has no wheel files).

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_wheel_filenames
        >>> mapping = fetch_pypi_wheel_filenames("numpy")  # doctest: +SKIP

        ```
    """
    metadata = fetch_data(url=f"https://pypi.org/pypi/{package}/json", timeout=10)
    result: dict[str, tuple[str, ...]] = {}
    for version, files in metadata["releases"].items():
        result[version] = tuple(
            file["filename"] for file in (files or []) if file.get("packagetype") == "bdist_wheel"
        )
    return result


@lru_cache
def fetch_pypi_versions(
    package: str,
    reverse: bool = False,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> tuple[str, ...]:
    r"""Get the package versions available on PyPI.

    The package versions are read from PyPI.

    Args:
        package: The package name.
        reverse: If ``False``, sort in ascending order; if ``True``,
            sort in descending order.
        start_date: If specified, only the versions released on or
            after this date are returned. The date can be a
            ``date`` object or an ISO 8601 formatted string
            e.g. ``'2024-01-01'``.
        end_date: If specified, only the versions released on or
            before this date are returned. The date can be a
            ``date`` object or an ISO 8601 formatted string
            e.g. ``'2024-12-31'``.

    Returns:
        A list containing the sorted version strings.

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_versions
        >>> versions = fetch_pypi_versions("requests")  # doctest: +SKIP
        >>> versions = fetch_pypi_versions(
        ...     "requests", start_date="2024-01-01", end_date="2024-12-31"
        ... )  # doctest: +SKIP

        ```
    """
    metadata = fetch_data(url=f"https://pypi.org/pypi/{package}/json", timeout=10)
    releases = metadata["releases"]
    versions = releases.keys()
    if start_date is not None or end_date is not None:
        start = _to_date(start_date) if start_date is not None else None
        end = _to_date(end_date) if end_date is not None else None
        versions = []
        for version, files in releases.items():
            released = _release_date(files)
            if released is None:
                continue
            if start is not None and released < start:
                continue
            if end is not None and released > end:
                continue
            versions.append(version)
    return tuple(sorted(versions, reverse=reverse))
