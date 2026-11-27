r"""Contain the functions and classes to install packages.

``install_package`` installs a package as requested, and
``install_package_closest_version`` first resolves the closest
compatible version (``feu.compat``). An ``Installer`` (``pip`` or
``uv``) builds one command that installs into the interpreter that runs
``feu``, after a dependency resolver (``feu.install.resolver``) added
the requirements that the package needs. The installers and the
resolvers are registered in registries that can be extended.
"""

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
