r"""Contain platform utilities."""

from __future__ import annotations

__all__ = ["get_current_arch", "get_current_os"]

import platform

_OS_NAMES = {"linux": "linux", "darwin": "macos", "windows": "windows"}
_ARCH_NAMES = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "arm64", "arm64": "arm64"}


def get_current_os() -> str | None:
    r"""Return the current OS name using the registry's vocabulary.

    The value returned by ``platform.system()`` is mapped to one of
    ``"linux"``, ``"macos"``, or ``"windows"``.

    Returns:
        The OS name, or ``None`` if it is not recognized.

    Example:
        ```pycon
        >>> from feu.utils.platform import get_current_os
        >>> get_current_os()  # doctest: +SKIP
        'linux'

        ```
    """
    return _OS_NAMES.get(platform.system().lower())


def get_current_arch() -> str | None:
    r"""Return the current CPU architecture using the registry's
    vocabulary.

    The value returned by ``platform.machine()`` is mapped to one of
    ``"x86_64"`` or ``"arm64"``.

    Returns:
        The architecture name, or ``None`` if it is not recognized.

    Example:
        ```pycon
        >>> from feu.utils.platform import get_current_arch
        >>> get_current_arch()  # doctest: +SKIP
        'x86_64'

        ```
    """
    return _ARCH_NAMES.get(platform.machine().lower())
