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
    "TorchDependencyResolver",
    "XarrayDependencyResolver",
]

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from packaging.version import Version

from feu.utils.package import PackageDependency

if TYPE_CHECKING:
    from feu.utils.package import Package

logger = logging.getLogger(__name__)


class BaseDependencyResolver(ABC):
    r"""Define the base class for pip-compatible package dependency
    resolvers.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import DependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = DependencyResolver()
    >>> resolver
    DependencyResolver()
    >>> deps = resolver.resolve(Package(name="my_package", version="1.2.3"))
    >>> deps
    [PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=None)]

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

        >>> from feu.install.pip.resolver2 import DependencyResolver, TorchDependencyResolver
        >>> from feu.utils.package import Package
        >>> obj1 = DependencyResolver()
        >>> obj2 = DependencyResolver()
        >>> obj3 = TorchDependencyResolver()
        >>> obj1.equal(obj2)
        True
        >>> obj1.equal(obj3)
        False

        ```
        """

    @abstractmethod
    def resolve(self, package: Package) -> list[PackageDependency]:
        r"""Find the dependency packages to install a specific package.

        Args:
            package: The target package to install.

        Returns:
            The list of package dependencies.

        Example usage:

        ```pycon

        >>> from feu.install.pip.resolver2 import DependencyResolver
        >>> from feu.utils.package import Package
        >>> resolver = DependencyResolver()
        >>> deps = resolver.resolve(Package(name="my_package", version="1.2.3"))
        >>> deps
        [PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=None)]

        ```
        """


class DependencyResolver(BaseDependencyResolver):
    r"""Define the default package dependency resolver.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import DependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = DependencyResolver()
    >>> resolver
    DependencyResolver()
    >>> deps = resolver.resolve(Package(name="my_package", version="1.2.3"))
    >>> deps
    [PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=None)]

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any) -> bool:
        return type(self) is type(other)

    def resolve(self, package: Package) -> list[PackageDependency]:
        return [package.to_package_dependency()]


class JaxDependencyResolver(DependencyResolver):
    r"""Implement the ``jax`` dependency resolver.

    ``numpy`` 2.0 support was added in ``jax`` 0.4.26.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import JaxDependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = JaxDependencyResolver()
    >>> resolver
    JaxDependencyResolver()
    >>> deps = resolver.resolve(Package(name="jax", version="0.4.26"))
    >>> deps
    [PackageDependency(name='jax', version_specifiers=['==0.4.26'], extras=None),
     PackageDependency(name='jaxlib', version_specifiers=['==0.4.26'], extras=None)]

    ```
    """

    def resolve(self, package: Package) -> list[PackageDependency]:
        deps = super().resolve(package)
        deps.append(PackageDependency("jaxlib", version_specifiers=[f"=={package.version}"]))
        ver = Version(package.version)
        if ver < Version("0.4.26"):
            deps.append(PackageDependency("numpy", version_specifiers=["<2.0.0"]))
        if Version("0.4.9") <= ver <= Version("0.4.11"):
            # https://github.com/google/jax/issues/17693
            deps.append(PackageDependency("ml_dtypes", version_specifiers=["<=0.2.0"]))
        return deps


class Numpy2DependencyResolver(DependencyResolver):
    r"""Define a dependency resolver to work with packages that did not
    pin ``numpy<2.0`` and are not fully compatible with numpy 2.0.

    https://github.com/numpy/numpy/issues/26191 indicates the packages
    that are compatible with numpy 2.0.

    Args:
        min_version: The first version that is fully compatible with
            numpy 2.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import Numpy2DependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = Numpy2DependencyResolver(min_version="1.2.3")
    >>> resolver
    Numpy2DependencyResolver(min_version=1.2.3)
    >>> deps = resolver.resolve(Package(name="my_package", version="1.2.3"))
    >>> deps
    [PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=None)]

    ```
    """

    def __init__(self, min_version: str) -> None:
        self._min_version = min_version

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(min_version={self._min_version})"

    def equal(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._min_version == other._min_version

    def resolve(self, package: Package) -> list[PackageDependency]:
        deps = super().resolve(package)
        if Version(package.version) < Version(self._min_version):
            deps.append(PackageDependency("numpy", version_specifiers=["<2.0.0"]))
        return deps


class MatplotlibDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``matplotlib`` dependency resolver.

    ``numpy`` 2.0 support was added in ``matplotlib`` 3.8.4.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import MatplotlibDependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = MatplotlibDependencyResolver()
    >>> resolver
    MatplotlibDependencyResolver(min_version=3.8.4)
    >>> deps = resolver.resolve(Package(name="matplotlib", version="3.8.4"))
    >>> deps
    [PackageDependency(name='matplotlib', version_specifiers=['==3.8.4'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="3.8.4")


class PandasDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``pandas`` dependency resolver.

    ``numpy`` 2.0 support was added in ``pandas`` 2.2.2.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import PandasDependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = PandasDependencyResolver()
    >>> resolver
    PandasDependencyResolver(min_version=2.2.2)
    >>> deps = resolver.resolve(Package(name="pandas", version="2.2.2"))
    >>> deps
    [PackageDependency(name='pandas', version_specifiers=['==2.2.2'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="2.2.2")


class PyarrowDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``pyarrow`` dependency resolver.

    ``numpy`` 2.0 support was added in ``pyarrow`` 16.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import PyarrowDependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = PyarrowDependencyResolver()
    >>> resolver
    PyarrowDependencyResolver(min_version=16.0)
    >>> deps = resolver.resolve(Package(name="pyarrow", version="16.0"))
    >>> deps
    [PackageDependency(name='pyarrow', version_specifiers=['==16.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="16.0")


class ScipyDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``scipy`` dependency resolver.

    ``numpy`` 2.0 support was added in ``scipy`` 1.13.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import ScipyDependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = ScipyDependencyResolver()
    >>> resolver
    ScipyDependencyResolver(min_version=1.13.0)
    >>> deps = resolver.resolve(Package(name="scipy", version="1.13.0"))
    >>> deps
    [PackageDependency(name='scipy', version_specifiers=['==1.13.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="1.13.0")


class TorchDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``torch`` dependency resolver.

    ``numpy`` 2.0 support was added in ``torch`` 2.3.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import TorchDependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = TorchDependencyResolver()
    >>> resolver
    TorchDependencyResolver(min_version=2.3.0)
    >>> deps = resolver.resolve(Package(name="torch", version="2.3.0"))
    >>> deps
    [PackageDependency(name='torch', version_specifiers=['==2.3.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="2.3.0")


class XarrayDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``xarray`` dependency resolver.

    ``numpy`` 2.0 support was added in ``xarray`` 2024.6.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import XarrayDependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = XarrayDependencyResolver()
    >>> resolver
    XarrayDependencyResolver(min_version=2024.6.0)
    >>> deps = resolver.resolve(Package(name="xarray", version="2024.6.0"))
    >>> deps
    [PackageDependency(name='xarray', version_specifiers=['==2024.6.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="2024.6.0")
