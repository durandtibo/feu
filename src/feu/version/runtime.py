r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = ["get_package_version", "get_python_major_minor"]

import sys
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version

from packaging.version import Version


def get_package_version(package: str) -> Version | None:
    r"""Get the package version.

    Args:
        package: The package name.

    Returns:
        The package version.

    Example usage:

    ```pycon

    >>> from feu.version import get_package_version
    >>> get_package_version("pytest")
    <Version('...')>

    ```
    """
    try:
        return Version(version(package))
    except PackageNotFoundError:
        return None


@lru_cache
def get_python_major_minor() -> str:
    r"""Get the MAJOR.MINOR version of the current python.

    Returns:
        The MAJOR.MINOR version of the current python.

    Example usage:

    ```pycon

    >>> from feu.version import get_python_major_minor
    >>> get_python_major_minor()  # doctest: +SKIP

    ```
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}"
