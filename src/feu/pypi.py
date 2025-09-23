r"""Contain PyPI utility functions."""

from __future__ import annotations

__all__ = ["get_pypi_versions"]

from functools import lru_cache

from feu.imports import check_requests, is_requests_available

if is_requests_available():  # pragma: no cover
    import requests


@lru_cache
def get_pypi_versions(package: str) -> tuple[str, ...]:
    r"""Get the package versions available on PyPI.

    The package versions are read from PyPI.

    Args:
        package: The package name.

    Returns:
        A list containing the version strings.

    Example usage:

    ```pycon

    >>> from feu.pypi import get_pypi_versions
    >>> versions = get_pypi_versions("requests")  # doctest: +SKIP

    ```
    """
    check_requests()
    data = requests.get(url=f"https://pypi.org/pypi/{package}/json", timeout=10).json()
    return tuple(sorted(data["releases"].keys(), reverse=True))
