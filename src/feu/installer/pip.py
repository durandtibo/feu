from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from coola.utils.format import repr_indent, repr_mapping

from feu.install import run_bash_command

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class BaseInstaller(ABC):
    r"""Define the base class to implement a pip package installer."""

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    @abstractmethod
    def install(self, packages: Sequence[str], args: str = "-U") -> None:
        r"""Install the given package version.

        Args:
            version: The target version to install.
        """


class PipInstaller(BaseInstaller):
    r"""TODO."""

    def install(self, packages: Sequence[str], args: str = "-U") -> None:
        run_bash_command(f"pip install {args} {' '.join(packages)}")


class PipxInstaller(BaseInstaller):
    r"""TODO."""

    def install(self, packages: Sequence[str], args: str = "-U") -> None:
        run_bash_command(f"pipx install {args} {' '.join(packages)}")


class UvInstaller(BaseInstaller):
    r"""TODO."""

    def install(self, packages: Sequence[str], args: str = "") -> None:
        run_bash_command(f"uv pip install {args} {' '.join(packages)}")


class BaseResolver(ABC):
    r"""Define the base class to implement a pip package installer."""

    @abstractmethod
    def resolve(self, version: str) -> tuple[str, ...]:
        r"""Install the given package version.

        Args:
            version: The target version to install.
        """


class DefaultResolver(BaseResolver):
    def __init__(self, package: str) -> None:
        self._package = package

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(package={self._package})"

    def resolve(self, version: str) -> tuple[str, ...]:
        return (f"{self._package}=={version}",)


class BasePackageInstaller(ABC):
    r"""Define the base class to implement a package installer."""

    @abstractmethod
    def install(self, version: str, args: str = "") -> None:
        r"""Install the given package version.

        Args:
            version: The target version to install.
        """


class PackageInstaller(BasePackageInstaller):
    r"""Implement a generic package installer.

    Args:
        package: The name of the package to install.
    """

    def __init__(self, resolver: BaseResolver, installer: BaseInstaller) -> None:
        self._resolver = resolver
        self._installer = installer

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"resolver": self._resolver, "installer": self._installer}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def install(self, version: str, args: str = "") -> None:
        self._installer.install(packages=self._resolver.resolve(version), args=args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    installers = [
        PackageInstaller(resolver=DefaultResolver("numpy"), installer=PipInstaller()),
        PackageInstaller(resolver=DefaultResolver("numpy"), installer=PipxInstaller()),
        PackageInstaller(resolver=DefaultResolver("numpy"), installer=UvInstaller()),
    ]
    for installer in installers:
        logger.info(installer)
        installer.install("2.3.1")
