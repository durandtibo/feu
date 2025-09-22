r"""Contain utility functions to install packages."""

from __future__ import annotations

__all__ = ["install_package"]

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
