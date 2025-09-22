r"""Contain functionalities to install packages with pip or compatible
package installers."""

from __future__ import annotations

__all__ = [
    "BaseCommandGenerator",
    "BaseDependencyResolver",
    "DependencyResolver",
    "JaxDependencyResolver",
    "MatplotlibDependencyResolver",
    "Numpy2DependencyResolver",
    "PandasDependencyResolver",
    "PipCommandGenerator",
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
