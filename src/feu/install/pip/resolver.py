r"""Contain pip compatible package dependency resolvers."""

from __future__ import annotations

__all__ = [
    "BaseDependencyResolver",
    "DependencyResolver",
    "DependencyResolverRegistry",
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
from typing import TYPE_CHECKING, Any, ClassVar

from packaging.version import Version

from feu.utils.package import PackageDependency

if TYPE_CHECKING:
    from feu.utils.package import PackageSpec

logger: logging.Logger = logging.getLogger(__name__)


class BaseDependencyResolver(ABC):
    r"""Define the base class for pip-compatible package dependency
    resolvers.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import DependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = DependencyResolver()
    >>> resolver
    DependencyResolver()
    >>> deps = resolver.resolve(PackageSpec(name="my_package", version="1.2.3"))
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

        >>> from feu.install.pip.resolver import DependencyResolver, TorchDependencyResolver
        >>> from feu.utils.package import PackageSpec
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
    def resolve(self, package: PackageSpec) -> list[PackageDependency]:
        r"""Find the dependency packages to install a specific package.

        Args:
            package: The target package to install.

        Returns:
            The list of package dependencies.

        Example usage:

        ```pycon

        >>> from feu.install.pip.resolver import DependencyResolver
        >>> from feu.utils.package import PackageSpec
        >>> resolver = DependencyResolver()
        >>> deps = resolver.resolve(PackageSpec(name="my_package", version="1.2.3"))
        >>> deps
        [PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=None)]

        ```
        """


class DependencyResolver(BaseDependencyResolver):
    r"""Define the default package dependency resolver.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import DependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = DependencyResolver()
    >>> resolver
    DependencyResolver()
    >>> deps = resolver.resolve(PackageSpec(name="my_package", version="1.2.3"))
    >>> deps
    [PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=None)]

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any) -> bool:
        return type(self) is type(other)

    def resolve(self, package: PackageSpec) -> list[PackageDependency]:
        return [package.to_package_dependency()]


class JaxDependencyResolver(DependencyResolver):
    r"""Implement the ``jax`` dependency resolver.

    ``numpy`` 2.0 support was added in ``jax`` 0.4.26.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import JaxDependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = JaxDependencyResolver()
    >>> resolver
    JaxDependencyResolver()
    >>> deps = resolver.resolve(PackageSpec(name="jax", version="0.4.26"))
    >>> deps
    [PackageDependency(name='jax', version_specifiers=['==0.4.26'], extras=None),
     PackageDependency(name='jaxlib', version_specifiers=['==0.4.26'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="jax", version="0.4.25"))
    >>> deps
    [PackageDependency(name='jax', version_specifiers=['==0.4.25'], extras=None),
     PackageDependency(name='jaxlib', version_specifiers=['==0.4.25'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

    ```
    """

    def resolve(self, package: PackageSpec) -> list[PackageDependency]:
        deps = super().resolve(package)
        if package.version is None:
            msg = f"Missing package version for {package.name}"
            raise RuntimeError(msg)
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

    >>> from feu.install.pip.resolver import Numpy2DependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = Numpy2DependencyResolver(min_version="1.2.3")
    >>> resolver
    Numpy2DependencyResolver(min_version=1.2.3)
    >>> deps = resolver.resolve(PackageSpec(name="my_package", version="1.2.3"))
    >>> deps
    [PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="my_package", version="1.2.2"))
    >>> deps
    [PackageDependency(name='my_package', version_specifiers=['==1.2.2'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

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

    def resolve(self, package: PackageSpec) -> list[PackageDependency]:
        deps = super().resolve(package)
        if package.version is None:
            msg = f"Missing package version for {package.name}"
            raise RuntimeError(msg)
        if Version(package.version) < Version(self._min_version):
            deps.append(PackageDependency("numpy", version_specifiers=["<2.0.0"]))
        return deps


class MatplotlibDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``matplotlib`` dependency resolver.

    ``numpy`` 2.0 support was added in ``matplotlib`` 3.8.4.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import MatplotlibDependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = MatplotlibDependencyResolver()
    >>> resolver
    MatplotlibDependencyResolver(min_version=3.8.4)
    >>> deps = resolver.resolve(PackageSpec(name="matplotlib", version="3.8.4"))
    >>> deps
    [PackageDependency(name='matplotlib', version_specifiers=['==3.8.4'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="matplotlib", version="3.8.3"))
    >>> deps
    [PackageDependency(name='matplotlib', version_specifiers=['==3.8.3'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="3.8.4")


class PandasDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``pandas`` dependency resolver.

    ``numpy`` 2.0 support was added in ``pandas`` 2.2.2.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import PandasDependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = PandasDependencyResolver()
    >>> resolver
    PandasDependencyResolver(min_version=2.2.2)
    >>> deps = resolver.resolve(PackageSpec(name="pandas", version="2.2.2"))
    >>> deps
    [PackageDependency(name='pandas', version_specifiers=['==2.2.2'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="pandas", version="2.2.1"))
    >>> deps
    [PackageDependency(name='pandas', version_specifiers=['==2.2.1'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="2.2.2")


class PyarrowDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``pyarrow`` dependency resolver.

    ``numpy`` 2.0 support was added in ``pyarrow`` 16.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import PyarrowDependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = PyarrowDependencyResolver()
    >>> resolver
    PyarrowDependencyResolver(min_version=16.0)
    >>> deps = resolver.resolve(PackageSpec(name="pyarrow", version="16.0"))
    >>> deps
    [PackageDependency(name='pyarrow', version_specifiers=['==16.0'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="pyarrow", version="15.0"))
    >>> deps
    [PackageDependency(name='pyarrow', version_specifiers=['==15.0'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="16.0")


class ScipyDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``scipy`` dependency resolver.

    ``numpy`` 2.0 support was added in ``scipy`` 1.13.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import ScipyDependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = ScipyDependencyResolver()
    >>> resolver
    ScipyDependencyResolver(min_version=1.13.0)
    >>> deps = resolver.resolve(PackageSpec(name="scipy", version="1.13.0"))
    >>> deps
    [PackageDependency(name='scipy', version_specifiers=['==1.13.0'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="scipy", version="1.12.0"))
    >>> deps
    [PackageDependency(name='scipy', version_specifiers=['==1.12.0'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="1.13.0")


class SklearnDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``scikit-learn`` dependency resolver.

    ``numpy`` 2.0 support was added in ``scikit-learn`` 1.4.2.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import SklearnDependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = SklearnDependencyResolver()
    >>> resolver
    SklearnDependencyResolver(min_version=1.4.2)
    >>> deps = resolver.resolve(PackageSpec(name="scikit-learn", version="1.4.2"))
    >>> deps
    [PackageDependency(name='scikit-learn', version_specifiers=['==1.4.2'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="scikit-learn", version="1.4.1"))
    >>> deps
    [PackageDependency(name='scikit-learn', version_specifiers=['==1.4.1'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="1.4.2")


class TorchDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``torch`` dependency resolver.

    ``numpy`` 2.0 support was added in ``torch`` 2.3.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import TorchDependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = TorchDependencyResolver()
    >>> resolver
    TorchDependencyResolver(min_version=2.3.0)
    >>> deps = resolver.resolve(PackageSpec(name="torch", version="2.3.0"))
    >>> deps
    [PackageDependency(name='torch', version_specifiers=['==2.3.0'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="torch", version="2.2.0"))
    >>> deps
    [PackageDependency(name='torch', version_specifiers=['==2.2.0'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="2.3.0")


class XarrayDependencyResolver(Numpy2DependencyResolver):
    r"""Implement the ``xarray`` dependency resolver.

    ``numpy`` 2.0 support was added in ``xarray`` 2024.6.0.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver import XarrayDependencyResolver
    >>> from feu.utils.package import PackageSpec
    >>> resolver = XarrayDependencyResolver()
    >>> resolver
    XarrayDependencyResolver(min_version=2024.6.0)
    >>> deps = resolver.resolve(PackageSpec(name="xarray", version="2024.6.0"))
    >>> deps
    [PackageDependency(name='xarray', version_specifiers=['==2024.6.0'], extras=None)]
    >>> deps = resolver.resolve(PackageSpec(name="xarray", version="2024.5.0"))
    >>> deps
    [PackageDependency(name='xarray', version_specifiers=['==2024.5.0'], extras=None),
     PackageDependency(name='numpy', version_specifiers=['<2.0.0'], extras=None)]

    ```
    """

    def __init__(self) -> None:
        super().__init__(min_version="2024.6.0")


class DependencyResolverRegistry:
    r"""Implement the main dependency resolver registry.

    The dependency resolvers are indexed by name.
    """

    registry: ClassVar[dict[str, BaseDependencyResolver]] = {
        "jax": JaxDependencyResolver(),
        "matplotlib": MatplotlibDependencyResolver(),
        "pandas": PandasDependencyResolver(),
        "pyarrow": PyarrowDependencyResolver(),
        "scikit-learn": SklearnDependencyResolver(),
        "scipy": ScipyDependencyResolver(),
        "sklearn": SklearnDependencyResolver(),
        "torch": TorchDependencyResolver(),
        "xarray": XarrayDependencyResolver(),
    }

    @classmethod
    def add_resolver(
        cls, package: PackageSpec, resolver: BaseDependencyResolver, exist_ok: bool = False
    ) -> None:
        r"""Add a dependency resolver for a given package.

        Args:
            package: The package specification.
            resolver: The resolver used for the given package.
            exist_ok: If ``False``, ``RuntimeError`` is raised if the
                package already exists. This parameter should be set
                to ``True`` to overwrite the resolver for a package.

        Raises:
            RuntimeError: if a dependency resolver is already registered for the
                package name and ``exist_ok=False``.

        Example usage:

        ```pycon

        >>> from feu.install.pip.resolver import (
        ...     DependencyResolverRegistry,
        ...     TorchDependencyResolver,
        ... )
        >>> from feu.utils.package import PackageSpec
        >>> DependencyResolverRegistry.add_resolver(
        ...     PackageSpec("torch"), TorchDependencyResolver(), exist_ok=True
        ... )

        ```
        """
        if package.name in cls.registry and not exist_ok:
            msg = (
                f"A dependency resolver is already registered for the package "
                f"{package.name}. Please use `exist_ok=True` if you want to overwrite the "
                "dependency resolver for this package"
            )
            raise RuntimeError(msg)
        cls.registry[package.name] = resolver

    @classmethod
    def has_resolver(cls, package: PackageSpec) -> bool:
        r"""Indicate if a dependency resolver is registered for the given
        package specification.

        Args:
            package: The package specification.

        Returns:
            ``True`` if a dependency resolver is registered,
                otherwise ``False``.

        Example usage:

        ```pycon

        >>> from feu.install.pip.resolver import DependencyResolverRegistry
        >>> from feu.utils.package import PackageSpec
        >>> DependencyResolverRegistry.has_resolver(PackageSpec("torch"))
        True

        ```
        """
        return package.name in cls.registry

    @classmethod
    def find_resolver(cls, package: PackageSpec) -> BaseDependencyResolver:
        r"""Find the relevant dependency resolver for the given package.

        Args:
            package: The package specification.

        Returns:
            The dependency resolver for the package.

        Example usage:

        ```pycon

        >>> from feu.install.pip.resolver import DependencyResolverRegistry
        >>> from feu.utils.package import PackageSpec
        >>> resolver = DependencyResolverRegistry.find_resolver(PackageSpec("torch"))
        >>> resolver
        TorchDependencyResolver(min_version=2.3.0)

        ```
        """
        return cls.registry.get(package.name, DependencyResolver())
