r"""Contain package installers."""

from __future__ import annotations

__all__ = [
    "BaseInstaller",
    "InstallerRegistry",
    "get_available_installers",
    "install_package",
    "is_pip_available",
    "is_pipx_available",
    "is_uv_available",
]

from feu.installer.installer import BaseInstaller
from feu.installer.registry import InstallerRegistry
from feu.installer.utils import (
    get_available_installers,
    install_package,
    is_pip_available,
    is_pipx_available,
    is_uv_available,
)
