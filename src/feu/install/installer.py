r"""Contain the base class to implement a package installer."""

from __future__ import annotations

__all__ = ["BaseInstaller"]

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseInstaller(ABC):
    r"""Define the base class to implement a package installer.

    Example usage:

    ```pycon

    >>> from feu.install.pip import PipInstaller
    >>> installer = PipInstaller()
    >>> installer.install(package="pandas", version="2.2.2")  # doctest: +SKIP

    ```
    """

    @abstractmethod
    def install(self, package: str, version: str, args: str = "") -> None:
        r"""Install the given package version.

        Args:
            package: The name of the package.
            version: The target version to install.
            args: Optional arguments to pass to the package installer.
                The list of valid arguments depend on the package
                installer.

        Example usage:

        ```pycon

        >>> from feu.install.pip import PipInstaller
        >>> installer = PipInstaller()
        >>> installer.install(package="pandas", version="2.2.2")  # doctest: +SKIP

        ```
        """
