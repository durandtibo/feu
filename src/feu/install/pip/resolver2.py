r"""Contain pip compatible package dependency resolvers."""

from __future__ import annotations

__all__ = [
    "BaseDependencyResolver",
    "DependencyResolver",
]

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from feu.utils.package import Package, PackageDependency

logger = logging.getLogger(__name__)


class BaseDependencyResolver(ABC):
    r"""Define the base class for pip-compatible package dependency resolvers.

    Example usage:

    ```pycon

    >>> from feu.install.pip.resolver2 import DependencyResolver
    >>> from feu.utils.package import Package
    >>> resolver = DependencyResolver()
    >>> resolver
    DependencyResolver()
    >>> deps = resolver.resolve(Package(name="numpy", version="2.3.1"))
    >>> deps
    [PackageDependency(name='numpy', version_specifiers=['==2.3.1'], extras=None)]

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
        >>> deps = resolver.resolve(Package(name="numpy", version="2.3.1"))
        >>> deps
        [PackageDependency(name='numpy', version_specifiers=['==2.3.1'], extras=None)]

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
    >>> deps = resolver.resolve(Package(name="numpy", version="2.3.1"))
    >>> deps
    [PackageDependency(name='numpy', version_specifiers=['==2.3.1'], extras=None)]

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any) -> bool:
        return isinstance(other, self.__class__)

    def resolve(self, package: Package) -> list[PackageDependency]:
        return [package.to_package_dependency()]
