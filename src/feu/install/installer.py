r"""Contain the base class to implement a package installer."""

from __future__ import annotations

__all__ = ["BaseInstaller"]

import logging
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

if TYPE_CHECKING:
    from feu.utils.package import PackageSpec

logger: logging.Logger = logging.getLogger(__name__)


class BaseInstaller(ABC):
    r"""Define the base class to implement a package installer.

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

    @abstractmethod
    def equal(self, other: Any) -> bool:
        r"""Indicate if two installers are equal or not.

        Args:
            other: The other object to compare.

        Returns:
            ``True`` if the two installers are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from feu.install.pip import PipInstaller
        >>> from feu.utils.package import PackageSpec
        >>> obj1 = PipInstaller()
        >>> obj2 = PipInstaller()
        >>> obj3 = PipInstaller("-U")
        >>> obj1.equal(obj2)
        True
        >>> obj1.equal(obj3)
        False

        ```
        """

    @abstractmethod
    def install(self, package: PackageSpec) -> None:
        r"""Install the given package.

        Args:
            package: The package specification of the package to install.

        Example usage:

        ```pycon

        >>> from feu.install.pip import PipInstaller
        >>> from feu.utils.package import PackageSpec
        >>> installer = PipInstaller()
        >>> installer.install(PackageSpec(name="pandas", version="2.2.2"))  # doctest: +SKIP

        ```
        """

    @classmethod
    @abstractmethod
    def instantiate_with_arguments(cls, arguments: str) -> Self:
        r"""Instantiate an installer instance with custom arguments.

        Args:
            arguments: The installer arguments.

        Returns:
            An instantiated installer.

        Example usage:

        ```pycon

        >>> from feu.install.pip import PipInstaller
        >>> installer = PipInstaller.instantiate_with_arguments("-U")
        >>> installer
        PipInstaller(arguments='-U')

        ```
        """
