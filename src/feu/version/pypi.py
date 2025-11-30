r"""Contain PyPI utility functions."""

from __future__ import annotations

__all__ = ["fetch_pypi_versions"]

from functools import lru_cache

from feu.utils.http import fetch_data


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

    Example usage:

    ```pycon

    >>> from feu.version import fetch_pypi_versions
    >>> versions = fetch_pypi_versions("requests")  # doctest: +SKIP

    ```
    """
    metadata = fetch_data(url=f"https://pypi.org/pypi/{package}/json", timeout=10)
    return tuple(sorted(metadata["releases"].keys(), reverse=reverse))
