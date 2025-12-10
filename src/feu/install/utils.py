r"""Contain utility functions to install packages."""

from __future__ import annotations

__all__ = [
    "install_package",
    "install_package_closest_version",
    "is_pip_available",
    "is_pipx_available",
    "is_uv_available",
]

import shutil
from functools import lru_cache
from typing import TYPE_CHECKING

from feu.install import InstallerRegistry
from feu.package import find_closest_version
from feu.version import get_python_major_minor

if TYPE_CHECKING:
    from feu.utils.installer import InstallerSpec
    from feu.utils.package import PackageSpec


def install_package(installer: InstallerSpec, package: PackageSpec) -> None:
    r"""Install a package with the specified installer.

    Args:
        installer: The installer specification.
        package: The package specification.

    Example usage:

    ```pycon

    >>> from feu.install import install_package
    >>> from feu.utils.installer import InstallerSpec
    >>> from feu.utils.package import PackageSpec
    >>> install_package(
    ...     installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.2.2")
    ... )  # doctest: +SKIP

    ```
    """
    InstallerRegistry.install(installer=installer, package=package)


def install_package_closest_version(installer: InstallerSpec, package: PackageSpec) -> None:
    r"""Install a package and associated packages by using the secified
    installer.

    This function finds the closest valid version if the specified
    version is not compatible.

    Args:
        installer: The installer specification.
        package: The package specification.

    Raises:
        RuntimeError: If no package version is specified.

    Example usage:

    ```pycon

    >>> from feu.install import install_package_closest_version
    >>> from feu.utils.installer import InstallerSpec
    >>> from feu.utils.package import PackageSpec
    >>> install_package_closest_version(
    ...     installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.2.2")
    ... )  # doctest: +SKIP

    ```
    """
    pkg_version = package.version
    if pkg_version is None:
        msg = f"A package version must be specified for {package.name}"
        raise RuntimeError(msg)
    install_package(
        installer=installer,
        package=package.with_version(
            find_closest_version(
                pkg_name=package.name,
                pkg_version=pkg_version,
                python_version=get_python_major_minor(),
            )
        ),
    )


@lru_cache(1)
def is_pip_available() -> bool:
    r"""Check if ``pip`` is available.

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
    r"""Check if ``pipx`` is available.

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
    r"""Check if ``uv`` is available.

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
