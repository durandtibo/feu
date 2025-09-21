r"""Contain functionalities to install packages with pip or compatible
package installers."""

from __future__ import annotations

__all__ = [
    "BaseDependencyResolver",
    "BasePackageInstaller",
    "DependencyResolver",
    "MatplotlibDependencyResolver",
    "Numpy2DependencyResolver",
    "PandasDependencyResolver",
    "PipPackageInstaller",
    "PipxPackageInstaller",
    "PyarrowDependencyResolver",
    "ScipyDependencyResolver",
    "SklearnDependencyResolver",
    "UvPackageInstaller",
]

from feu.installer.pip.installer import (
    BasePackageInstaller,
    PipPackageInstaller,
    PipxPackageInstaller,
    UvPackageInstaller,
)
from feu.installer.pip.resolver import (
    BaseDependencyResolver,
    DependencyResolver,
    MatplotlibDependencyResolver,
    Numpy2DependencyResolver,
    PandasDependencyResolver,
    PyarrowDependencyResolver,
    ScipyDependencyResolver,
    SklearnDependencyResolver,
)
