r"""Contain the functions to install all the compatible versions of a
package."""

from __future__ import annotations

__all__ = ["InstallResult", "get_installable_versions", "install_all_versions"]

import logging
from typing import TYPE_CHECKING, NamedTuple

from packaging.requirements import Requirement

from feu.compat import get_default_compat_registry
from feu.install.api import install_package
from feu.utils.package import PackageSpec
from feu.version import (
    fetch_pypi_versions,
    filter_stable_versions,
    filter_valid_versions,
    sort_versions,
)

if TYPE_CHECKING:
    from datetime import date

    from feu.compat import Target
    from feu.install.installer import InstallerSpec

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


def get_installable_versions(
    pkg_name: str, target: Target, *, start_date: date | str | None = None
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
        The stable versions of the package that are valid for the
            given target, in PEP 440 order (ascending).

    Example:
        ```pycon
        >>> from feu.compat import Target
        >>> from feu.install import get_installable_versions
        >>> versions = get_installable_versions(
        ...     "numpy", target=Target(python_version="3.11")
        ... )  # doctest: +SKIP

        ```
    """
    registry = get_default_compat_registry()
    versions = filter_stable_versions(
        filter_valid_versions(fetch_pypi_versions(pkg_name, start_date=start_date))
    )
    return sort_versions(
        [
            version
            for version in versions
            if registry.is_valid_version(pkg_name=pkg_name, pkg_version=version, target=target)
        ]
    )


def install_all_versions(
    installer: InstallerSpec,
    package: str,
    target: Target,
    *,
    start_date: date | str | None = None,
) -> InstallResult:
    r"""Install all the versions of a package that are compatible with a
    target, one after the other.

    A failure to install one version does not stop the installation of
    the remaining versions. The failure is logged.

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

    Raises:
        packaging.requirements.InvalidRequirement: If ``package`` is
            not a valid requirement.

    Example:
        ```pycon
        >>> from feu.compat import Target
        >>> from feu.install import InstallerSpec, install_all_versions
        >>> result = install_all_versions(
        ...     installer=InstallerSpec("pip"),
        ...     package="pandas[performance]",
        ...     target=Target(python_version="3.11"),
        ... )  # doctest: +SKIP

        ```
    """
    requirement = Requirement(package)
    logger.info("Installing %s...", package)
    installed: list[str] = []
    failed: list[str] = []
    versions = get_installable_versions(requirement.name, target=target, start_date=start_date)
    logger.info("Installable versions for %s: %s", package, versions)
    for version in versions:
        spec = PackageSpec(
            name=requirement.name, version=version, extras=sorted(requirement.extras)
        )
        (installed if _try_install(installer, spec) else failed).append(version)
    return InstallResult(installed=installed, failed=failed)


def _try_install(installer: InstallerSpec, package: PackageSpec) -> bool:
    r"""Try to install a package, returning whether it succeeded.

    Any exception raised by the installation is logged and not
    propagated.

    Args:
        installer: The installer specification.
        package: The package specification.

    Returns:
        ``True`` if the installation succeeded, otherwise ``False``.
    """
    try:
        install_package(installer=installer, package=package)
    except Exception:
        logger.exception("failed to install %s", package)
        return False
    return True
