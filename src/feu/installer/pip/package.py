r"""Contain package installers."""

from __future__ import annotations

__all__ = ["BasePackageInstaller", "PackageInstaller"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from feu.utils.command import run_bash_command

if TYPE_CHECKING:
    from feu.installer.pip.command import BaseCommandGenerator
    from feu.installer.pip.resolver import BaseDependencyResolver


class BasePackageInstaller(ABC):
    r"""Define the base class to implement a package installer.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import DependencyResolver, PackageInstaller, PipCommandGenerator
    >>> installer = PackageInstaller(
    ...     resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    ... )
    >>> installer
    PackageInstaller(resolver=DependencyResolver(package=numpy), command=PipCommandGenerator())
    >>> installer.install("2.3.1")  # doctest: +SKIP

    ```
    """

    @abstractmethod
    def install(self, version: str, args: str = "") -> None:
        r"""Install the given version of the package.

        Args:
            version: The target version to install.
            args: Optional arguments to pass to the package installer.
                The list of valid arguments depend on the package
                installer.

        Example usage:

        ```pycon

        >>> from feu.installer.pip import DependencyResolver, PackageInstaller, PipCommandGenerator
        >>> installer = PackageInstaller(
        ...     resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
        ... )
        >>> installer.install("2.3.1")  # doctest: +SKIP

        ```
        """


class PackageInstaller(BasePackageInstaller):
    r"""Implement a generic package installer.

    Args:
        resolver: The dependency resolver to get the list of packages to install.
        command: The command generator to install the packages.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import DependencyResolver, PackageInstaller, PipCommandGenerator
    >>> installer = PackageInstaller(
    ...     resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    ... )
    >>> installer
    PackageInstaller(resolver=DependencyResolver(package=numpy), command=PipCommandGenerator())
    >>> installer.install("2.3.1")  # doctest: +SKIP

    ```
    """

    def __init__(self, resolver: BaseDependencyResolver, command: BaseCommandGenerator) -> None:
        self._resolver = resolver
        self._command = command

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(resolver={self._resolver}, command={self._command})"

    def install(self, version: str, args: str = "") -> None:
        run_bash_command(
            self._command.generate(packages=self._resolver.resolve(version), args=args)
        )
