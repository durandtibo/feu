r"""Contain utility functions to install packages."""

from __future__ import annotations

__all__ = ["install_package", "is_pip_available", "is_pipx_available"]

import shutil

from feu.imports import is_package_available
from feu.installer import InstallerRegistry


def install_package(installer: str, package: str, version: str, args: str = "") -> None:
    r"""Install a package and associated packages by using the secified
    installer.

    Args:
        installer: The package installer name to use to install the
            packages.
        package: The target package to install.
        version: The target version of the package to install.
        args: Optional arguments to pass to the package installer.
            The list of valid arguments depend on the package
            installer.

    Example usage:

    ```pycon

    >>> from feu.installer import install_package
    >>> install_package(installer="pip", package="pandas", version="2.2.2")  # doctest: +SKIP

    ```
    """
    InstallerRegistry.install(installer=installer, package=package, version=version, args=args)


def is_pip_available() -> bool:
    """Check if ``pip`` is available.

    Returns:
        ``True`` if ``pip`` is available, otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.installer import is_pip_available
    >>> is_pip_available()

    ```
    """
    return is_package_available("pip")


def is_pipx_available() -> bool:
    """Check if ``pipx`` is available.

    Returns:
        ``True`` if ``pipx`` is available, otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.installer import is_pipx_available
    >>> is_pipx_available()

    ```
    """
    return shutil.which("pipx") is not None
