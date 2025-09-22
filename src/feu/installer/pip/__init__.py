r"""Contain functionalities to install packages with pip or compatible
package installers."""

from __future__ import annotations

__all__ = [
    "BaseDependencyResolver",
    "BasePackageInstaller",
    "DependencyResolver",
    "JaxDependencyResolver",
    "MatplotlibDependencyResolver",
    "Numpy2DependencyResolver",
    "PandasDependencyResolver",
    "PipPackageInstaller",
    "PipxPackageInstaller",
    "PyarrowDependencyResolver",
    "ScipyDependencyResolver",
    "SklearnDependencyResolver",
    "TorchDependencyResolver",
    "UvPackageInstaller",
    "XarrayDependencyResolver",
]

from feu.installer.pip.package import (
    BasePackageInstaller,
    PipPackageInstaller,
    PipxPackageInstaller,
    UvPackageInstaller,
)
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
