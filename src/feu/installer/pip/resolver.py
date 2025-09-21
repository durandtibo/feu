r"""Contain pip compatible package dependency resolvers."""

from __future__ import annotations

__all__ = ["BaseDependencyResolver", "DependencyResolver"]

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseDependencyResolver(ABC):
    r"""Define the base class to implement a pip package installer.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import DependencyResolver
    >>> resolver = DependencyResolver("numpy")
    >>> resolver
    DependencyResolver(package=numpy)
    >>> out = resolver.resolve("2.3.1")
    >>> out
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
        >>> out = resolver.resolve("2.3.1")
        >>> out
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
    >>> out = resolver.resolve("2.3.1")
    >>> out
    ('numpy==2.3.1',)

    ```
    """

    def __init__(self, package: str) -> None:
        self._package = package

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(package={self._package})"

    def resolve(self, version: str) -> tuple[str, ...]:
        return (f"{self._package}=={version}",)
