r"""Contain package installers."""

from __future__ import annotations

__all__ = ["BaseInstaller", "InstallerRegistry", "install_package", "is_pip_available"]

from feu.installer.installer import BaseInstaller
from feu.installer.registry import InstallerRegistry
from feu.installer.utils import install_package, is_pip_available
