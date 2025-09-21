r"""Contain functionalities to install packages with pip or compatible
package installers."""

from __future__ import annotations

__all__ = [
    "BaseDependencyResolver",
    "BasePackageInstaller",
    "DependencyResolver",
    "PipPackageInstaller",
]

from feu.installer.pip.installer import BasePackageInstaller, PipPackageInstaller
from feu.installer.pip.resolver import BaseDependencyResolver, DependencyResolver
