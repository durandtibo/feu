r"""Contain utility functions to manage installers."""

from __future__ import annotations

__all__ = ["InstallerSpec"]

from dataclasses import dataclass


@dataclass
class InstallerSpec:
    r"""Define a dataclass to represent an installer specification.

    Args:
        name: The installer name.
        arguments: A string containing optional installer arguments.

    Example usage:

    ```pycon

    >>> from feu.utils.installer import InstallerSpec
    >>> installer1 = InstallerSpec("pip")
    >>> installer1
    InstallerSpec(name='pip', arguments='')
    >>> installer2 = InstallerSpec("pip", arguments="-U")
    >>> installer2
    InstallerSpec(name='pip', arguments='-U')

    ```
    """

    name: str
    arguments: str = ""
