r"""Contain package installers."""

from __future__ import annotations

__all__ = ["BasePackageInstaller", "PackageInstaller", "create_package_installer_mapping"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from feu.install.pip.resolver import (
    JaxDependencyResolver,
    MatplotlibDependencyResolver,
    PandasDependencyResolver,
    PyarrowDependencyResolver,
    ScipyDependencyResolver,
    SklearnDependencyResolver,
    TorchDependencyResolver,
    XarrayDependencyResolver,
)
from feu.utils.command import run_bash_command

if TYPE_CHECKING:
    from feu.install.pip.command import BaseCommandGenerator
    from feu.install.pip.resolver import BaseDependencyResolver


class BasePackageInstaller(ABC):
    r"""Define the base class to implement a package installer.

    Example usage:

    ```pycon

    >>> from feu.install.pip.command import PipCommandGenerator
    >>> from feu.install.pip.package import PackageInstaller
    >>> from feu.install.pip.resolver import DependencyResolver
    >>> installer = PackageInstaller(
    ...     resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    ... )
    >>> installer
    PackageInstaller(resolver=DependencyResolver(package=numpy), command=PipCommandGenerator())
    >>> installer.install("2.3.1")  # doctest: +SKIP

    ```
    """

    @abstractmethod
    def equal(self, other: Any) -> bool:
        r"""Indicate if two package installers are equal or not.

        Args:
            other: The other object to compare.

        Returns:
            ``True`` if the two package installers are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from feu.install.pip.command import PipCommandGenerator
        >>> from feu.install.pip.package import PackageInstaller
        >>> from feu.install.pip.resolver import DependencyResolver
        >>> obj1 = PackageInstaller(
        ...     resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
        ... )
        >>> obj2 = PackageInstaller(
        ...     resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
        ... )
        >>> obj3 = PackageInstaller(
        ...     resolver=DependencyResolver("torch"), command=PipCommandGenerator()
        ... )
        >>> obj1.equal(obj2)
        True
        >>> obj1.equal(obj3)
        False

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

        >>> from feu.install.pip.command import PipCommandGenerator
        >>> from feu.install.pip.package import PackageInstaller
        >>> from feu.install.pip.resolver import DependencyResolver
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

    >>> from feu.install.pip.command import PipCommandGenerator
    >>> from feu.install.pip.package import PackageInstaller
    >>> from feu.install.pip.resolver import DependencyResolver
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

    def equal(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._resolver.equal(other._resolver) and self._command.equal(other._command)

    def install(self, version: str, args: str = "") -> None:
        run_bash_command(
            self._command.generate(packages=self._resolver.resolve(version), args=args)
        )


def create_package_installer_mapping(
    command: BaseCommandGenerator,
) -> dict[str, BasePackageInstaller]:
    r"""Create the default package installer mapping.

    Args:
        command: The command generator uses to install the command.

    Returns:
        The mapping package installers, where the keys are the package
            names and the values are the package installers.

    Example usage:

    ```pycon

    >>> from feu.install.pip.command import PipCommandGenerator
    >>> from feu.install.pip.package import create_package_installer_mapping
    >>> installers = create_package_installer_mapping(command=PipCommandGenerator())
    >>> installers
    {'jax': PackageInstaller(resolver=JaxDependencyResolver(), command=PipCommandGenerator()),
     ...
     'xarray': PackageInstaller(resolver=XarrayDependencyResolver(), command=PipCommandGenerator())}

    ```
    """
    return {
        "jax": PackageInstaller(resolver=JaxDependencyResolver(), command=command),
        "matplotlib": PackageInstaller(resolver=MatplotlibDependencyResolver(), command=command),
        "pandas": PackageInstaller(resolver=PandasDependencyResolver(), command=command),
        "pyarrow": PackageInstaller(resolver=PyarrowDependencyResolver(), command=command),
        "scikit-learn": PackageInstaller(resolver=SklearnDependencyResolver(), command=command),
        "scipy": PackageInstaller(resolver=ScipyDependencyResolver(), command=command),
        "sklearn": PackageInstaller(resolver=SklearnDependencyResolver(), command=command),
        "torch": PackageInstaller(resolver=TorchDependencyResolver(), command=command),
        "xarray": PackageInstaller(resolver=XarrayDependencyResolver(), command=command),
    }
