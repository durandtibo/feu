r"""Contain pip compatible package dependency resolvers."""

from __future__ import annotations

__all__ = [
    "BaseDependencyResolver",
    "DependencyResolver",
    "MatplotlibDependencyResolver",
    "Numpy2DependencyResolver",
    "PandasDependencyResolver",
    "PyarrowDependencyResolver",
]

import logging
from abc import ABC, abstractmethod

from packaging.version import Version

logger = logging.getLogger(__name__)


class BaseDependencyResolver(ABC):
    r"""Define the base class to implement a pip package installer.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import DependencyResolver
    >>> resolver = DependencyResolver("numpy")
    >>> resolver
    DependencyResolver(package=numpy)
    >>> deps = resolver.resolve("2.3.1")
    >>> deps
    ('numpy==2.3.1',)

    ```
    """

    @abstractmethod
    def resolve(self, version: str) -> tuple[str, ...]:
        r"""Find the dependency packages and their versions to install
        the specific version of a package.

        Args:
            version: The target version of the package to install.

        Returns:
            The tuple of packages and versions constraints.

        Example usage:

        ```pycon

        >>> from feu.installer.pip import DependencyResolver
        >>> resolver = DependencyResolver("numpy")
        >>> deps = resolver.resolve("2.3.1")
        >>> deps
        ('numpy==2.3.1',)

        ```
        """


class DependencyResolver(BaseDependencyResolver):
    r"""Define the default package dependency resolver.

    Args:
        package: The name of the target package to install.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import DependencyResolver
    >>> resolver = DependencyResolver("numpy")
    >>> resolver
    DependencyResolver(package=numpy)
    >>> deps = resolver.resolve("2.3.1")
    >>> deps
    ('numpy==2.3.1',)

    ```
    """

    def __init__(self, package: str) -> None:
        self._package = package

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(package={self._package})"

    def resolve(self, version: str) -> tuple[str, ...]:
        return (f"{self._package}=={version}",)


class Numpy2DependencyResolver(BaseDependencyResolver):
    r"""Define a dependency resolver to work with packages that did not
    pin ``numpy<2.0`` and are not fully compatible with numpy 2.0.

    https://github.com/numpy/numpy/issues/26191 indicates the packages
    that are compatible with numpy 2.0.

    Args:
        package: The name of the package.
        min_version: The first version that is fully compatible with
            numpy 2.0.
    """

    def __init__(self, package: str, min_version: str) -> None:
        self._package = package
        self._min_version = min_version

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def resolve(self, version: str) -> tuple[str, ...]:
        deps = [f"{self._package}=={version}"]
        if Version(version) < Version(self._min_version):
            deps.append("numpy<2.0.0")
        return tuple(deps)


class MatplotlibDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``matplotlib`` dependency resolver.

    ``numpy`` 2.0 support was added in ``matplotlib`` 3.8.4.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import MatplotlibDependencyResolver
    >>> resolver = MatplotlibDependencyResolver()
    >>> resolver
    MatplotlibDependencyResolver()
    >>> deps = resolver.resolve("3.8.4")
    >>> deps
    ('matplotlib==3.8.4',)

    ```
    """

    def __init__(self) -> None:
        super().__init__(package="matplotlib", min_version="3.8.4")


class PandasDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``pandas`` dependency resolver.

    ``numpy`` 2.0 support was added in ``pandas`` 2.2.2.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import PandasDependencyResolver
    >>> resolver = PandasDependencyResolver()
    >>> resolver
    PandasDependencyResolver()
    >>> deps = resolver.resolve("2.2.2")
    >>> deps
    ('pandas==2.2.2',)

    ```
    """

    def __init__(self) -> None:
        super().__init__(package="pandas", min_version="2.2.2")


class PyarrowDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``pyarrow`` dependency resolver.

    ``numpy`` 2.0 support was added in ``pyarrow`` 16.0.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import PyarrowDependencyResolver
    >>> resolver = PyarrowDependencyResolver()
    >>> resolver
    PyarrowDependencyResolver()
    >>> deps = resolver.resolve("16.0")
    >>> deps
    ('pyarrow==16.0',)

    ```
    """

    def __init__(self) -> None:
        super().__init__(package="pyarrow", min_version="16.0")
