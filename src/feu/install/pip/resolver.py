r"""Contain pip compatible package dependency resolvers."""

from __future__ import annotations

__all__ = [
    "BaseDependencyResolver",
    "DependencyResolver",
    "JaxDependencyResolver",
    "MatplotlibDependencyResolver",
    "Numpy2DependencyResolver",
    "PandasDependencyResolver",
    "PyarrowDependencyResolver",
    "ScipyDependencyResolver",
    "SklearnDependencyResolver",
    "TorchDependencyResolver",
    "XarrayDependencyResolver",
]

import logging
from abc import ABC, abstractmethod
from typing import Any

from packaging.version import Version

logger = logging.getLogger(__name__)


class BaseDependencyResolver(ABC):
    r"""Define the base class to implement a pip package installer.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import DependencyResolver
    >>> resolver = DependencyResolver("numpy")
    >>> resolver
    DependencyResolver(package=numpy)
    >>> deps = resolver.resolve("2.3.1")
    >>> deps
    ('numpy==2.3.1',)

    ```
    """

    @abstractmethod
    def equal(self, other: Any) -> bool:
        r"""Indicate if two dependency resolvers are equal or not.

        Args:
            other: The other object to compare.

        Returns:
            ``True`` if the two dependency resolvers are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from feu.install.pip.resolver import DependencyResolver, TorchDependencyResolver
        >>> obj1 = DependencyResolver("numpy")
        >>> obj2 = DependencyResolver("numpy")
        >>> obj3 = TorchDependencyResolver()
        >>> obj1.equal(obj2)
        True
        >>> obj1.equal(obj3)
        False

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

        >>> from feu.install.pip.resolver import DependencyResolver
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

    >>> from feu.install.pip.resolver import DependencyResolver
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

    def equal(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._package == other._package

    def resolve(self, version: str) -> tuple[str, ...]:
        return (f"{self._package}=={version}",)


class JaxDependencyResolver(BaseDependencyResolver):
    r"""Implement the ``jax`` dependency resolver.

    ``numpy`` 2.0 support was added in ``jax`` 0.4.26.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import JaxDependencyResolver
    >>> resolver = JaxDependencyResolver()
    >>> resolver
    JaxDependencyResolver()
    >>> deps = resolver.resolve("0.4.26")
    >>> deps
    ('jax==0.4.26', 'jaxlib==0.4.26')

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any) -> bool:
        return isinstance(other, self.__class__)

    def resolve(self, version: str) -> tuple[str, ...]:
        deps = [f"jax=={version}", f"jaxlib=={version}"]
        ver = Version(version)
        if ver < Version("0.4.26"):
            deps.append("numpy<2.0.0")
        if Version("0.4.9") <= ver <= Version("0.4.11"):
            # https://github.com/google/jax/issues/17693
            deps.append("ml_dtypes<=0.2.0")
        return tuple(deps)


class Numpy2DependencyResolver(BaseDependencyResolver):
    r"""Define a dependency resolver to work with packages that did not
    pin ``numpy<2.0`` and are not fully compatible with numpy 2.0.

    https://github.com/numpy/numpy/issues/26191 indicates the packages
    that are compatible with numpy 2.0.

    Args:
        package: The name of the package.
        min_version: The first version that is fully compatible with
            numpy 2.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import Numpy2DependencyResolver
    >>> resolver = Numpy2DependencyResolver(package="my_package", min_version="1.2.3")
    >>> resolver
    Numpy2DependencyResolver()
    >>> deps = resolver.resolve("1.2.3")
    >>> deps
    ('my_package==1.2.3',)

    ```
    """

    def __init__(self, package: str, min_version: str) -> None:
        self._package = package
        self._min_version = min_version

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._package == other._package and self._min_version == other._min_version

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

    >>> from feu.install.pip.resolver import MatplotlibDependencyResolver
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

    >>> from feu.install.pip.resolver import PandasDependencyResolver
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

    >>> from feu.install.pip.resolver import PyarrowDependencyResolver
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


class ScipyDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``scipy`` dependency resolver.

    ``numpy`` 2.0 support was added in ``scipy`` 1.13.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import ScipyDependencyResolver
    >>> resolver = ScipyDependencyResolver()
    >>> resolver
    ScipyDependencyResolver()
    >>> deps = resolver.resolve("1.13.0")
    >>> deps
    ('scipy==1.13.0',)

    ```
    """

    def __init__(self) -> None:
        super().__init__(package="scipy", min_version="1.13.0")


class SklearnDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``scikit-learn`` dependency resolver.

    ``numpy`` 2.0 support was added in ``scikit-learn`` 1.4.2.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import SklearnDependencyResolver
    >>> resolver = SklearnDependencyResolver()
    >>> resolver
    SklearnDependencyResolver()
    >>> deps = resolver.resolve("1.4.2")
    >>> deps
    ('scikit-learn==1.4.2',)

    ```
    """

    def __init__(self) -> None:
        super().__init__(package="scikit-learn", min_version="1.4.2")


class TorchDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``torch`` dependency resolver.

    ``numpy`` 2.0 support was added in ``torch`` 2.3.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import TorchDependencyResolver
    >>> resolver = TorchDependencyResolver()
    >>> resolver
    TorchDependencyResolver()
    >>> deps = resolver.resolve("2.3.0")
    >>> deps
    ('torch==2.3.0',)

    ```
    """

    def __init__(self) -> None:
        super().__init__(package="torch", min_version="2.3.0")


class XarrayDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``xarray`` dependency resolver.

    ``numpy`` 2.0 support was added in ``xarray`` 2024.6.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import XarrayDependencyResolver
    >>> resolver = XarrayDependencyResolver()
    >>> resolver
    XarrayDependencyResolver()
    >>> deps = resolver.resolve("2024.6.0")
    >>> deps
    ('xarray==2024.6.0',)

    ```
    """

    def __init__(self) -> None:
        super().__init__(package="xarray", min_version="2024.6.0")
