r"""Contain utility functions to manage installers."""

from __future__ import annotations

__all__ = ["InstallerSpec", "normalize_arguments"]

import shlex
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def normalize_arguments(arguments: str | Sequence[str]) -> tuple[str, ...]:
    r"""Normalize the arguments of an installer to a tuple of strings.

    A string is split once with ``shlex.split`` (POSIX rules, on every
    platform). A sequence of strings is converted to a tuple and is not
    split again.

    Args:
        arguments: The installer arguments, as one string e.g.
            ``"-U --pre"`` or as a sequence of arguments.

    Returns:
        The arguments as a tuple of strings.

    Raises:
        TypeError: If ``arguments`` is neither a string nor a sequence
            of strings.

    Example:
        ```pycon
        >>> from feu.utils.installer import normalize_arguments
        >>> normalize_arguments("-U --pre")
        ('-U', '--pre')
        >>> normalize_arguments(["--index-url", "https://example.com/my index"])
        ('--index-url', 'https://example.com/my index')

        ```
    """
    if isinstance(arguments, str):
        return tuple(shlex.split(arguments))
    if isinstance(arguments, (list, tuple)) and all(isinstance(arg, str) for arg in arguments):
        return tuple(arguments)
    msg = (
        "installer arguments must be a string or a list/tuple of strings but received "
        f"{arguments!r}"
    )
    raise TypeError(msg)


@dataclass(frozen=True, init=False)
class InstallerSpec:
    r"""Define a dataclass to represent an installer specification.

    Args:
        name: The installer name.
        arguments: The optional installer arguments. A string is
            split once with ``shlex.split``; a list or a tuple of
            strings is used as is. The arguments are stored as a
            tuple.

    Raises:
        TypeError: If ``arguments`` is neither a string nor a list or
            tuple of strings.

    Example:
        ```pycon
        >>> from feu.utils.installer import InstallerSpec
        >>> installer1 = InstallerSpec("pip")
        >>> installer1
        InstallerSpec(name='pip', arguments=())
        >>> installer2 = InstallerSpec("pip", arguments="-U --pre")
        >>> installer2
        InstallerSpec(name='pip', arguments=('-U', '--pre'))
        >>> installer3 = InstallerSpec("pip", arguments=["-U", "--pre"])
        >>> installer3 == installer2
        True

        ```
    """

    name: str
    arguments: tuple[str, ...]

    def __init__(self, name: str, arguments: str | Sequence[str] = ()) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "arguments", normalize_arguments(arguments))
