r"""Define the compatibility target key used to look up package
version constraints."""

from __future__ import annotations

__all__ = ["Target"]

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    r"""Identify the environment a package compatibility constraint
    applies to.

    Args:
        python_version: The Python version, e.g. ``"3.11"``.
        free_threaded: ``True`` for a free-threaded (no-GIL) Python
            build, e.g. ``3.14t``. Defaults to ``False``.
        os: The operating system, e.g. ``"linux"``, ``"macos"``,
            ``"windows"``. ``None`` means "any OS" when used as a
            registry entry, and "unspecified" when used as a lookup
            target.
        arch: The CPU architecture, e.g. ``"x86_64"``, ``"arm64"``.
            ``None`` means "any architecture" when used as a registry
            entry, and "unspecified" when used as a lookup target.

    Example:
        ```pycon
        >>> from feu.compat.target import Target
        >>> Target(python_version="3.14", free_threaded=True, os="linux", arch="x86_64")
        Target(python_version='3.14', free_threaded=True, os='linux', arch='x86_64')

        ```
    """

    python_version: str
    free_threaded: bool = False
    os: str | None = None
    arch: str | None = None
