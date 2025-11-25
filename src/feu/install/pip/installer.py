r"""Define the pip compatible installers."""

from __future__ import annotations

__all__ = ["BasePipInstaller", "PipInstaller", "PipxInstaller", "UvInstaller"]

import sys
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from feu.install.installer import BaseInstaller
from feu.install.pip.resolver import (
    DependencyResolverRegistry,
)
from feu.utils.command import run_bash_command

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.utils.package import PackageDependency, PackageSpec


class BasePipInstaller(BaseInstaller):
    r"""Define an intermediate base class to implement pip compatible
    package installer.

    Args:
        arguments: Optional arguments to pass to the package installer.
            The valid arguments depend on the package installer.

    Example usage (subclassing):

    ```pycon

    >>> from feu.install.pip.installer import BasePipInstaller
    >>> from feu.utils.package import PackageSpec, PackageDependency
    >>> class MyInstaller(BasePipInstaller):
    ...     def _generate_command(self, deps, args):
    ...         return f"echo Installing {', '.join(map(str, deps))} with args: {args}"
    ...
    >>> installer = MyInstaller(arguments="--verbose")
    >>> installer
    MyInstaller(arguments='--verbose')
    >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

    ```
    """

    def __init__(self, arguments: str = "") -> None:
        self._arguments = arguments.strip()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(arguments={self._arguments!r})"

    def equal(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._arguments == other._arguments

    def install(self, package: PackageSpec) -> None:
        deps = DependencyResolverRegistry.find_resolver(package).resolve(package)
        cmd = self._generate_command(deps=deps, args=self._arguments)
        cmd = " ".join(cmd.split())  # remove duplicate spaces
        run_bash_command(cmd)

    @classmethod
    def instantiate_with_arguments(cls, arguments: str) -> Self:
        return cls(arguments=arguments)

    @abstractmethod
    def _generate_command(self, deps: Sequence[PackageDependency], args: str) -> str:
        r"""Generate the command to run to install the dependencies.

        Args:
            deps: The dependencies to install.
            args: Arguments to pass to the package installer.
                The valid arguments depend on the package installer.

        Returns:
            A string containing the command to run to install the
                dependencies.
        """


class PipInstaller(BasePipInstaller):
    r"""Implement a pip package installer.

    Example usage:

    ```pycon

    >>> from feu.install.pip import PipInstaller
    >>> from feu.utils.package import PackageSpec
    >>> installer = PipInstaller()
    >>> installer
    PipInstaller(arguments='')
    >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

    ```
    """

    def _generate_command(self, deps: Sequence[PackageDependency], args: str) -> str:
        cmd_parts = ["pip", "install"]
        if args:
            cmd_parts.append(args)
        cmd_parts.extend(map(str, deps))
        return " ".join(cmd_parts)


class PipxInstaller(BasePipInstaller):
    r"""Implement a pipx package installer.

    Example usage:

    ```pycon

    >>> from feu.install.pip import PipxInstaller
    >>> from feu.utils.package import PackageSpec
    >>> installer = PipxInstaller()
    >>> installer
    PipxInstaller(arguments='')
    >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

    ```
    """

    def _generate_command(self, deps: Sequence[PackageDependency], args: str) -> str:
        cmd_parts = ["pipx", "install"]
        if args:
            cmd_parts.append(args)
        cmd_parts.extend(map(str, deps))
        return " ".join(cmd_parts)


class UvInstaller(BasePipInstaller):
    r"""Implement a uv package installer.

    Example usage:

    ```pycon

    >>> from feu.install.pip import UvInstaller
    >>> from feu.utils.package import PackageSpec
    >>> installer = UvInstaller()
    >>> installer
    UvInstaller(arguments='')
    >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

    ```
    """

    def _generate_command(self, deps: Sequence[PackageDependency], args: str) -> str:
        cmd_parts = ["uv", "pip", "install"]
        if args:
            cmd_parts.append(args)
        cmd_parts.extend(map(str, deps))
        return " ".join(cmd_parts)
