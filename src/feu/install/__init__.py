r"""Contain package installers."""

from __future__ import annotations

__all__ = [
    "BaseInstaller",
    "InstallerRegistry",
    "get_available_installers",
    "install_package",
    "install_package_closest_version",
    "is_pip_available",
    "is_pipx_available",
    "is_uv_available",
]

from feu.install.installer import BaseInstaller
from feu.install.registry import InstallerRegistry
from feu.install.utils import (
    get_available_installers,
    install_package,
    install_package_closest_version,
    is_pip_available,
    is_pipx_available,
    is_uv_available,
)
