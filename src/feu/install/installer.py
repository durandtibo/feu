r"""Contain the base class to implement a package install."""

from __future__ import annotations

__all__ = ["BaseInstaller"]

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseInstaller(ABC):
    r"""Define the base class to implement a package install.

    Example usage:

    ```pycon

    >>> from feu.install.pip import PipInstaller
    >>> install = PipInstaller()
    >>> install.install(package="pandas", version="2.2.2")  # doctest: +SKIP

    ```
    """

    @abstractmethod
    def install(self, package: str, version: str, args: str = "") -> None:
        r"""Install the given package version.

        Args:
            package: The name of the package.
            version: The target version to install.
            args: Optional arguments to pass to the package install.
                The list of valid arguments depend on the package
                install.

        Example usage:

        ```pycon

        >>> from feu.install.pip import PipInstaller
        >>> install = PipInstaller()
        >>> install.install(package="pandas", version="2.2.2")  # doctest: +SKIP

        ```
        """
