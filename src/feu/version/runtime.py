r"""Contain functions to get the version of an installed package."""

from __future__ import annotations

__all__ = ["get_package_version"]

from importlib.metadata import PackageNotFoundError, version

from packaging.version import InvalidVersion, Version


def get_package_version(package: str) -> Version | None:
    r"""Get the package version.

    Args:
        package: The package name.

    Returns:
        The package version, or ``None`` if the package is not
            installed or if its version is not a valid PEP 440
            version.

    Example:
        ```pycon
        >>> from feu.version import get_package_version
        >>> get_package_version("pytest")
        <Version('...')>

        ```
    """
    try:
        return Version(version(package))
    except (PackageNotFoundError, InvalidVersion):
        return None
