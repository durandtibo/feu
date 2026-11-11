r"""Contain package installers."""

from __future__ import annotations

__all__ = [
    "InstallResult",
    "Installer",
    "InstallerSpec",
    "PipInstaller",
    "UvInstaller",
    "get_default_installer_registry",
    "get_default_resolver_registry",
    "get_installable_versions",
    "install_all_versions",
    "install_package",
    "install_package_closest_version",
    "is_pip_available",
    "is_uv_available",
    "register_installer",
    "register_resolver",
]

from feu.install.all_versions import InstallResult, get_installable_versions, install_all_versions
from feu.install.api import install_package, install_package_closest_version
from feu.install.installer import (
    Installer,
    InstallerSpec,
    PipInstaller,
    UvInstaller,
    get_default_installer_registry,
    is_pip_available,
    is_uv_available,
    register_installer,
)
from feu.install.resolver import get_default_resolver_registry, register_resolver
