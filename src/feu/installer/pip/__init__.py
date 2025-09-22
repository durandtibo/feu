r"""Contain functionalities to install packages with pip or compatible
package installers."""

from __future__ import annotations

__all__ = [
    "BaseCommandGenerator",
    "BaseDependencyResolver",
    "BasePackageInstaller",
    "DependencyResolver",
    "JaxDependencyResolver",
    "MatplotlibDependencyResolver",
    "Numpy2DependencyResolver",
    "PackageInstaller",
    "PandasDependencyResolver",
    "PipCommandGenerator",
    "PipInstaller",
    "PipxCommandGenerator",
    "PyarrowDependencyResolver",
    "ScipyDependencyResolver",
    "SklearnDependencyResolver",
    "TorchDependencyResolver",
    "UvCommandGenerator",
    "XarrayDependencyResolver",
]

from feu.installer.pip.command import (
    BaseCommandGenerator,
    PipCommandGenerator,
    PipxCommandGenerator,
    UvCommandGenerator,
)
from feu.installer.pip.installer import PipInstaller
from feu.installer.pip.package import BasePackageInstaller, PackageInstaller
from feu.installer.pip.resolver import (
    BaseDependencyResolver,
    DependencyResolver,
    JaxDependencyResolver,
    MatplotlibDependencyResolver,
    Numpy2DependencyResolver,
    PandasDependencyResolver,
    PyarrowDependencyResolver,
    ScipyDependencyResolver,
    SklearnDependencyResolver,
    TorchDependencyResolver,
    XarrayDependencyResolver,
)
