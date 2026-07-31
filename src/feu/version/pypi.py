r"""Contain PyPI utility functions."""

from __future__ import annotations

__all__ = ["fetch_pypi_requires_python", "fetch_pypi_versions", "fetch_pypi_wheel_filenames"]

from functools import lru_cache

from feu.utils.http import fetch_data


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
def fetch_pypi_versions(package: str, reverse: bool = False) -> tuple[str, ...]:
    r"""Get the package versions available on PyPI.

    The package versions are read from PyPI.

    Args:
        package: The package name.
        reverse: If ``False``, sort in ascending order; if ``True``,
            sort in descending order.

    Returns:
        A list containing the sorted version strings.

    Example:
        ```pycon
        >>> from feu.version import fetch_pypi_versions
        >>> versions = fetch_pypi_versions("requests")  # doctest: +SKIP

        ```
    """
    metadata = fetch_data(url=f"https://pypi.org/pypi/{package}/json", timeout=10)
    return tuple(sorted(metadata["releases"].keys(), reverse=reverse))
