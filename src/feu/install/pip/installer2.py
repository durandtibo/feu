r"""Define the pip compatible installers."""

from __future__ import annotations

__all__ = ["BasePipInstaller", "PipInstaller"]

from abc import abstractmethod
from typing import TYPE_CHECKING

from feu.install.installer2 import BaseInstaller
from feu.install.pip.resolver2 import (
    DependencyResolverRegistry,
)
from feu.utils.command import run_bash_command

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.utils.package import PackageDependency, PackageSpec


class BasePipInstaller(BaseInstaller):
    """Define an intermediate base class to implement pip compatible
    package installer.

    Args:
        arguments: Optional arguments to pass to the package installer.
            The valid arguments depend on the package installer.
    """

    def __init__(self, arguments: str = "") -> None:
        self._arguments = arguments.strip()

    def install(self, package: PackageSpec) -> None:
        deps = DependencyResolverRegistry.find_resolver(package).resolve(package)
        cmd = self._generate_command(deps=deps, args=self._arguments)
        run_bash_command(cmd)

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
    """Implement a pip package installer."""

    def _generate_command(self, deps: Sequence[PackageDependency], args: str) -> str:
        return f"pip install {args} {' '.join(map(str, deps))}"
