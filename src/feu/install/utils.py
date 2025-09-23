r"""Contain utility functions to install packages."""

from __future__ import annotations

__all__ = ["install_package", "is_pip_available", "is_pipx_available"]

import shutil
from functools import lru_cache

from feu.install import InstallerRegistry


def install_package(installer: str, package: str, version: str, args: str = "") -> None:
    r"""Install a package and associated packages by using the secified
    install.

    Args:
        installer: The package installer name to use to install the
            packages.
        package: The target package to install.
        version: The target version of the package to install.
        args: Optional arguments to pass to the package installer.
            The list of valid arguments depend on the package
            install.

    Example usage:

    ```pycon

    >>> from feu.install import install_package
    >>> install_package(install="pip", package="pandas", version="2.2.2")  # doctest: +SKIP

    ```
    """
    InstallerRegistry.install(installer=installer, package=package, version=version, args=args)


@lru_cache(1)
def is_pip_available() -> bool:
    """Check if ``pip`` is available.

    Returns:
        ``True`` if ``pip`` is available, otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.install import is_pip_available
    >>> is_pip_available()

    ```
    """
    return shutil.which("pip") is not None


@lru_cache(1)
def is_pipx_available() -> bool:
    """Check if ``pipx`` is available.

    Returns:
        ``True`` if ``pipx`` is available, otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.install import is_pipx_available
    >>> is_pipx_available()

    ```
    """
    return shutil.which("pipx") is not None


@lru_cache(1)
def is_uv_available() -> bool:
    """Check if ``uv`` is available.

    Returns:
        ``True`` if ``uv`` is available, otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.install import is_uv_available
    >>> is_uv_available()

    ```
    """
    return shutil.which("uv") is not None


@lru_cache(1)
def get_available_installers() -> tuple[str, ...]:
    r"""Get the available installers.

    Returns:
        The available installers.

    Example usage:

    ```pycon

    >>> from feu.install import get_available_installers
    >>> get_available_installers()
    (...)

    ```
    """
    installers = []
    if is_pip_available():
        installers.append("pip")
    if is_pipx_available():
        installers.append("pipx")
    if is_uv_available():
        installers.append("uv")
    return tuple(installers)
