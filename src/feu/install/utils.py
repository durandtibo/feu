r"""Contain utility functions to install packages."""

from __future__ import annotations

__all__ = [
    "InstallResult",
    "get_installable_versions",
    "install_all_versions",
    "install_package",
    "install_package_closest_version",
    "install_packages_all_versions",
    "is_pip_available",
    "is_pipx_available",
    "is_uv_available",
]

import logging
import shutil
from functools import lru_cache
from typing import TYPE_CHECKING, NamedTuple

from feu.compat import Target, find_closest_version, get_default_registry
from feu.install import InstallerRegistry
from feu.utils.package import PackageSpec, extract_package_extras, extract_package_name
from feu.version import (
    fetch_pypi_versions,
    filter_stable_versions,
    filter_valid_versions,
    get_python_major_minor,
    sort_versions,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from feu.utils.installer import InstallerSpec

logger: logging.Logger = logging.getLogger(__name__)


class InstallResult(NamedTuple):
    r"""Represent the outcome of installing multiple versions of a
    package.

    Args:
        installed: The versions that were installed successfully.
        failed: The versions for which the installation failed.
    """

    installed: list[str]
    failed: list[str]


def install_package(installer: InstallerSpec, package: PackageSpec) -> None:
    r"""Install a package with the specified installer.

    Args:
        installer: The installer specification.
        package: The package specification.

    Example:
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
    r"""Install a package and associated packages by using the specified
    installer.

    This function finds the closest valid version if the specified
    version is not compatible.

    Args:
        installer: The installer specification.
        package: The package specification.

    Raises:
        RuntimeError: If no package version is specified.

    Example:
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
                target=Target(python_version=get_python_major_minor()),
            )
        ),
    )


def get_installable_versions(
    pkg_name: str, target: Target, start_date: date | str | None = None
) -> list[str]:
    r"""Get the stable package versions compatible with a target.

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        target: The compatibility target.
        start_date: If specified, only the versions released on or
            after this date are considered. The date can be a
            ``date`` object or an ISO 8601 formatted string
            e.g. ``'2024-01-01'``.

    Returns:
        The sorted list of stable versions of the package that are
            valid for the given target.

    Example:
        ```pycon
        >>> from feu.compat import Target
        >>> from feu.install import get_installable_versions
        >>> versions = get_installable_versions(
        ...     "numpy", target=Target(python_version="3.11")
        ... )  # doctest: +SKIP

        ```
    """
    registry = get_default_registry()
    versions = filter_stable_versions(
        filter_valid_versions(fetch_pypi_versions(pkg_name, start_date=start_date))
    )
    return [
        version
        for version in versions
        if registry.is_valid_version(pkg_name=pkg_name, pkg_version=version, target=target)
    ]


def install_all_versions(
    installer: InstallerSpec,
    package: str,
    target: Target,
    start_date: date | str | None = None,
) -> InstallResult:
    r"""Install all the versions of a package that are compatible with a
    target, one after the other.

    A failure to install one version does not stop the installation of
    the remaining versions.

    Args:
        installer: The installer specification.
        package: The package to install, optionally with extras
            e.g. ``"pandas[performance]"``.
        target: The compatibility target.
        start_date: If specified, only the versions released on or
            after this date are installed. The date can be a
            ``date`` object or an ISO 8601 formatted string
            e.g. ``'2024-01-01'``.

    Returns:
        The versions that were installed successfully and the
            versions for which the installation failed.

    Example:
        ```pycon
        >>> from feu.compat import Target
        >>> from feu.install import install_all_versions
        >>> from feu.utils.installer import InstallerSpec
        >>> result = install_all_versions(
        ...     installer=InstallerSpec("pip"),
        ...     package="pandas[performance]",
        ...     target=Target(python_version="3.11"),
        ... )  # doctest: +SKIP

        ```
    """
    pkg_name = extract_package_name(package)
    extras = extract_package_extras(package)
    logger.info(f"Installing {package}...")
    installed: list[str] = []
    failed: list[str] = []
    versions = sort_versions(
        get_installable_versions(pkg_name=pkg_name, target=target, start_date=start_date)
    )
    logger.info(f"Installable versions for {package}: {versions}")
    for version in versions:
        spec = PackageSpec(name=pkg_name, version=version, extras=extras or None)
        (installed if _try_install(installer, spec) else failed).append(version)
    return InstallResult(installed=installed, failed=failed)


def _try_install(installer: InstallerSpec, package: PackageSpec) -> bool:
    r"""Try to install a package, returning whether it succeeded."""
    try:
        install_package(installer=installer, package=package)
    except Exception:
        logger.exception(f"failed to install {package}")
        return False
    return True


def install_packages_all_versions(
    installer: InstallerSpec,
    packages: Sequence[str],
    target: Target,
    start_date: date | str | None = None,
) -> dict[str, InstallResult]:
    r"""Install all the versions of each package in a list that are
    compatible with a target.

    A failure to install one version of one package does not stop the
    installation of the remaining versions or packages.

    Args:
        installer: The installer specification.
        packages: The packages to install, optionally with extras
            e.g. ``"pandas[performance]"``.
        target: The compatibility target.
        start_date: If specified, only the versions released on or
            after this date are installed. The date can be a
            ``date`` object or an ISO 8601 formatted string
            e.g. ``'2024-01-01'``.

    Returns:
        A mapping of package to the versions that were installed
            successfully and the versions for which the installation
            failed.

    Example:
        ```pycon
        >>> from feu.compat import Target
        >>> from feu.install import install_packages_all_versions
        >>> from feu.utils.installer import InstallerSpec
        >>> results = install_packages_all_versions(
        ...     installer=InstallerSpec("pip"),
        ...     packages=["numpy", "pandas[performance]"],
        ...     target=Target(python_version="3.11"),
        ... )  # doctest: +SKIP

        ```
    """
    return {
        package: install_all_versions(
            installer=installer, package=package, target=target, start_date=start_date
        )
        for package in packages
    }


@lru_cache(1)
def is_pip_available() -> bool:
    r"""Check if ``pip`` is available.

    Returns:
        ``True`` if ``pip`` is available, otherwise ``False``.

    Example:
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

    Example:
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

    Example:
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

    Example:
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
