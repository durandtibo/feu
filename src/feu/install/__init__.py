r"""Contain package installers."""

from __future__ import annotations

__all__ = [
    "BaseInstaller",
    "InstallResult",
    "InstallerRegistry",
    "get_available_installers",
    "get_installable_versions",
    "install_all_versions",
    "install_package",
    "install_package_closest_version",
    "install_packages_all_versions",
    "is_pip_available",
    "is_pipx_available",
    "is_uv_available",
]

from feu.install.installer import BaseInstaller
from feu.install.registry import InstallerRegistry
from feu.install.utils import (
    InstallResult,
    get_available_installers,
    get_installable_versions,
    install_all_versions,
    install_package,
    install_package_closest_version,
    install_packages_all_versions,
    is_pip_available,
    is_pipx_available,
    is_uv_available,
)
