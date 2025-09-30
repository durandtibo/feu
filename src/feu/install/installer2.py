r"""Contain the base class to implement a package installer."""

from __future__ import annotations

__all__ = ["BaseInstaller"]

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from feu.utils.package import PackageSpec

logger = logging.getLogger(__name__)


class BaseInstaller(ABC):
    r"""Define the base class to implement a package installer.

    Example usage:

    ```pycon

    >>> from feu.install.pip.installer2 import PipInstaller
    >>> from feu.utils.package import PackageSpec
    >>> installer = PipInstaller()
    >>> installer
    PipInstaller(arguments='')
    >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

    ```
    """

    @abstractmethod
    def install(self, package: PackageSpec) -> None:
        r"""Install the given package.

        Args:
            package: The package specification of the package to install.

        Example usage:

        ```pycon

        >>> from feu.install.pip.installer2 import PipInstaller
        >>> from feu.utils.package import PackageSpec
        >>> installer = PipInstaller()
        >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

        ```
        """

    @classmethod
    @abstractmethod
    def instantiate_with_arguments(cls, arguments: str) -> BaseInstaller:
        r"""Instantiate an installer instance with custom arguments.

        Args:
            arguments: The installer arguments.

        Returns:
            An instantiated installer.
        """
