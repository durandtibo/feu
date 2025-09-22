r"""Contain pip compatible package installers."""

from __future__ import annotations

__all__ = [
    "BasePackageInstaller",
    "PipPackageInstaller",
    "PipxPackageInstaller",
    "UvPackageInstaller",
]

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from feu.utils.command import run_bash_command

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class BasePackageInstaller(ABC):
    r"""Define the base class to install packages with pip or compatible
    package installer.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import PipPackageInstaller
    >>> installer = PipPackageInstaller()
    >>> installer
    PipPackageInstaller()
    >>> installer.install(["numpy", "pandas>=2.0,<3.0"])  # doctest: +SKIP

    ```
    """

    @abstractmethod
    def install(self, packages: Sequence[str], args: str = "") -> None:
        r"""Install the specified packages.

        Args:
            packages: The tuple of packages to install. It is also
                possible to specify the version constraints.
            args: Optional arguments to pass to the package installer.
                The list of valid arguments depend on the package
                installer.

        Example usage:

        ```pycon

        >>> from feu.installer.pip import PipPackageInstaller
        >>> installer = PipPackageInstaller()
        >>> installer.install(["numpy", "pandas>=2.0,<3.0"])  # doctest: +SKIP

        ```
        """


class PipPackageInstaller(BasePackageInstaller):
    r"""Define a package installer that uses pip to install the packages.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import PipPackageInstaller
    >>> installer = PipPackageInstaller()
    >>> installer
    PipPackageInstaller()
    >>> installer.install(["numpy", "pandas>=2.0,<3.0"])  # doctest: +SKIP

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def install(self, packages: Sequence[str], args: str = "") -> None:
        if args != "":
            args = " " + args.strip()
        run_bash_command(f"pip install{args} {' '.join(packages)}")


class PipxPackageInstaller(BasePackageInstaller):
    r"""Define a package installer that uses pipx to install the
    packages.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import PipxPackageInstaller
    >>> installer = PipxPackageInstaller()
    >>> installer
    PipxPackageInstaller()
    >>> installer.install(["numpy", "pandas>=2.0,<3.0"])  # doctest: +SKIP

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def install(self, packages: Sequence[str], args: str = "") -> None:
        if args != "":
            args = " " + args.strip()
        run_bash_command(f"pipx install{args} {' '.join(packages)}")


class UvPackageInstaller(BasePackageInstaller):
    r"""Define a package installer that uses uv to install the packages.

    Example usage:

    ```pycon

    >>> from feu.installer.pip import UvPackageInstaller
    >>> installer = UvPackageInstaller()
    >>> installer
    UvPackageInstaller()
    >>> installer.install(["numpy", "pandas>=2.0,<3.0"])  # doctest: +SKIP

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def install(self, packages: Sequence[str], args: str = "") -> None:
        if args != "":
            args = " " + args.strip()
        run_bash_command(f"uv pip install{args} {' '.join(packages)}")
