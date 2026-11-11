r"""Contain the functions to install a package."""

from __future__ import annotations

__all__ = ["install_package", "install_package_closest_version"]

from typing import TYPE_CHECKING

from feu.compat import Target, find_closest_version, resolve_target
from feu.install.installer import get_default_installer_registry

if TYPE_CHECKING:
    from feu.install.installer import Installer, InstallerSpec
    from feu.utils.package import PackageSpec
    from feu.utils.registry import Registry


def install_package(
    installer: InstallerSpec,
    package: PackageSpec,
    *,
    registry: Registry[type[Installer]] | None = None,
) -> None:
    r"""Install a package with the specified installer.

    The package is installed as specified, without any version
    compatibility check. Use ``install_package_closest_version`` to
    install the closest compatible version.

    Args:
        installer: The installer specification.
        package: The package specification.
        registry: The installer registry. ``None`` means the default
            registry.

    Raises:
        RuntimeError: If no installer is registered for the installer
            name, or if the tool of the installer is not available.
        subprocess.CalledProcessError: If the installation command
            fails.

    Example:
        ```pycon
        >>> from feu.install import InstallerSpec, install_package
        >>> from feu.utils.package import PackageSpec
        >>> install_package(
        ...     installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.2.2")
        ... )  # doctest: +SKIP

        ```
    """
    registry = get_default_installer_registry() if registry is None else registry
    if installer.name not in registry:
        msg = (
            f"No installer is registered for the name {installer.name!r}. "
            f"Available installers: {registry.keys()}"
        )
        raise RuntimeError(msg)
    registry.find(installer.name)(arguments=installer.arguments).install(package)


def install_package_closest_version(
    installer: InstallerSpec,
    package: PackageSpec,
    *,
    target: Target | None = None,
    registry: Registry[type[Installer]] | None = None,
) -> None:
    r"""Install a package and associated packages by using the specified
    installer.

    This function finds the closest valid version if the specified
    version is not compatible with the target. By default, the target
    is the current environment: the Python version, the free-threaded
    flag, the OS and the CPU architecture.

    The package version is a version request: an exact version
    (``'2.0.2'``), a wildcard (``'2.*'``) or ``''`` for the latest
    version. A request is resolved to the latest compatible version. If
    that version lies in an open-ended range, the request itself is
    installed, so the installer picks the real latest release.

    Args:
        installer: The installer specification.
        package: The package specification.
        target: The compatibility target. ``None`` means the current
            environment (``resolve_target()``).
        registry: The installer registry. ``None`` means the default
            registry.

    Raises:
        RuntimeError: If no installer is registered for the installer
            name, or if the tool of the installer is not available.
        UnsupportedVersionError: If no version of the package is
            valid for the target, or if no known version satisfies a
            wildcard request.
        ValueError: If the package version is not a valid version
            request.
        subprocess.CalledProcessError: If the installation command
            fails.

    Example:
        ```pycon
        >>> from feu.install import InstallerSpec, install_package_closest_version
        >>> from feu.utils.package import PackageSpec
        >>> install_package_closest_version(
        ...     installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.2.2")
        ... )  # doctest: +SKIP

        ```
    """
    install_package(
        installer=installer,
        package=package.with_version(
            find_closest_version(
                pkg_name=package.name,
                pkg_version=package.version,
                target=resolve_target() if target is None else target,
            )
        ),
        registry=registry,
    )
