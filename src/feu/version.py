from __future__ import annotations

__all__ = ["get_package_version"]

from importlib.metadata import PackageNotFoundError, version

from packaging.version import Version


def get_package_version(package: str) -> Version | None:
    r"""Gets the package version.

    Args:
    ----
        package (str): Specifies the package name.

    Returns:
    -------
        ``packaging.version.Version``: The package version.

    Example usage:

    .. code-block:: pycon

        >>> from feu.version import get_package_version
        >>> get_package_version("pytest")
        <Version('...')>
    """
    try:
        return Version(version(package))
    except PackageNotFoundError:
        return None
