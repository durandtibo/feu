r"""Contain command generators to install packages."""

from __future__ import annotations

__all__ = [
    "BaseCommandGenerator",
    "PipCommandGenerator",
    "PipxCommandGenerator",
    "UvCommandGenerator",
]

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class BaseCommandGenerator(ABC):
    r"""Define the base class to generate a command to install packages
    with pip or compatible package installer.

    Example usage:

    ```pycon

    >>> from feu.install.pip.command import PipCommandGenerator
    >>> gen = PipCommandGenerator()
    >>> gen
    PipCommandGenerator()
    >>> cmd = gen.generate(["numpy", "pandas>=2.0,<3.0"])
    >>> cmd
    pip install numpy pandas>=2.0,<3.0

    ```
    """

    @abstractmethod
    def equal(self, other: Any) -> bool:
        r"""Indicate if two command generators are equal or not.

        Args:
            other: The other object to compare.

        Returns:
            ``True`` if the two command generators are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from feu.install.pip.command import PipCommandGenerator, PipxCommandGenerator
        >>> obj1 = PipCommandGenerator()
        >>> obj2 = PipCommandGenerator()
        >>> obj3 = PipxCommandGenerator()
        >>> obj1.equal(obj2)
        True
        >>> obj1.equal(obj3)
        False

        ```
        """

    @abstractmethod
    def generate(self, packages: Sequence[str], args: str = "") -> str:
        r"""Generate a command to install the specified packages.

        Args:
            packages: The tuple of packages to install. It is also
                possible to specify the version constraints.
            args: Optional arguments to pass to the package installer.
                The list of valid arguments depend on the package
                installer.

        Returns:
            The generated command.

        Example usage:

        ```pycon

        >>> from feu.install.pip.command import PipCommandGenerator
        >>> gen = PipCommandGenerator()
        >>> cmd = gen.generate(["numpy", "pandas>=2.0,<3.0"])
        >>> cmd
        pip install numpy pandas>=2.0,<3.0

        ```
        """


class PipCommandGenerator(BaseCommandGenerator):
    r"""Define a command generator for ``pip``.

    Example usage:

    ```pycon

    >>> from feu.install.pip.command import PipCommandGenerator
    >>> gen = PipCommandGenerator()
    >>> gen
    PipCommandGenerator()
    >>> cmd = gen.generate(["numpy", "pandas>=2.0,<3.0"])
    >>> cmd
    pip install numpy pandas>=2.0,<3.0

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any) -> bool:
        return isinstance(other, self.__class__)

    def generate(self, packages: Sequence[str], args: str = "") -> str:
        if args != "":
            args = " " + args.strip()
        return f"pip install{args} {' '.join(packages)}"


class PipxCommandGenerator(BaseCommandGenerator):
    r"""Define a command generator for ``pipx``.

    Example usage:

    ```pycon

    >>> from feu.install.pip.command import PipxCommandGenerator
    >>> gen = PipxCommandGenerator()
    >>> gen
    PipxCommandGenerator()
    >>> cmd = gen.generate(["numpy", "pandas>=2.0,<3.0"])
    >>> cmd
    pipx install numpy pandas>=2.0,<3.0

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any) -> bool:
        return isinstance(other, self.__class__)

    def generate(self, packages: Sequence[str], args: str = "") -> str:
        if args != "":
            args = " " + args.strip()
        return f"pipx install{args} {' '.join(packages)}"


class UvCommandGenerator(BaseCommandGenerator):
    r"""Define a command generator for ``uv``.

    Example usage:

    ```pycon

    >>> from feu.install.pip.command import UvCommandGenerator
    >>> gen = UvCommandGenerator()
    >>> gen
    UvCommandGenerator()
    >>> cmd = gen.generate(["numpy", "pandas>=2.0,<3.0"])
    >>> cmd
    uv pip install numpy pandas>=2.0,<3.0

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any) -> bool:
        return isinstance(other, self.__class__)

    def generate(self, packages: Sequence[str], args: str = "") -> str:
        if args != "":
            args = " " + args.strip()
        return f"uv pip install{args} {' '.join(packages)}"
