r"""Define the compatibility target key used to look up package version
constraints."""

from __future__ import annotations

__all__ = ["VALID_ARCH", "VALID_OS", "Target", "resolve_target"]

import re
from dataclasses import dataclass

from feu.utils.platform import (
    get_current_arch,
    get_current_os,
    get_python_version,
    is_free_threaded,
)

_PYTHON_VERSION_PATTERN = re.compile(r"^\d+\.\d+$")
VALID_OS = frozenset({"linux", "macos", "windows"})
VALID_ARCH = frozenset({"x86_64", "arm64"})


@dataclass(frozen=True)
class Target:
    r"""Identify the environment a package compatibility constraint
    applies to.

    Args:
        python_version: The Python version, e.g. ``"3.11"``. Must be a
            ``"major.minor"`` string, without a free-threaded ``t``
            suffix.
        free_threaded: ``True`` for a free-threaded (no-GIL) Python
            build, e.g. ``3.14t``. Defaults to ``False``.
        os: The operating system, e.g. ``"linux"``, ``"macos"``,
            ``"windows"``. ``None`` means "any OS" when used as a
            registry entry, and "unspecified" when used as a lookup
            target.
        arch: The CPU architecture, e.g. ``"x86_64"``, ``"arm64"``.
            ``None`` means "any architecture" when used as a registry
            entry, and "unspecified" when used as a lookup target.

    Raises:
        ValueError: if ``python_version`` is not a ``"major.minor"``
            string, or if ``os``/``arch`` is not one of the supported
            values.

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

    def __post_init__(self) -> None:
        if not _PYTHON_VERSION_PATTERN.match(self.python_version):
            msg = (
                f"invalid python_version {self.python_version!r}: expected a "
                "'major.minor' string, e.g. '3.11'"
            )
            raise ValueError(msg)
        if self.os is not None and self.os not in VALID_OS:
            msg = f"invalid os {self.os!r}: expected one of {sorted(VALID_OS)} or None"
            raise ValueError(msg)
        if self.arch is not None and self.arch not in VALID_ARCH:
            msg = f"invalid arch {self.arch!r}: expected one of {sorted(VALID_ARCH)} or None"
            raise ValueError(msg)


def resolve_target(
    python_version: str | None = None,
    free_threaded: bool | None = None,
    os: str | None = None,
    arch: str | None = None,
) -> Target:
    r"""Resolve a ``Target`` from optional, possibly partial inputs.

    If ``python_version`` ends with ``t``, the target is a
    free-threaded build. In that case, ``free_threaded=False`` is
    invalid because it contradicts the ``t`` suffix. Any unspecified
    argument falls back to the current interpreter/environment value.

    Args:
        python_version: The Python version, e.g. ``"3.11"`` or
            ``"3.14t"``. If not provided, the current python version
            is used.
        free_threaded: Whether the target is a free-threaded build.
            If not provided, it is inferred from ``python_version`` or
            the current interpreter's free-threaded status.
        os: The target OS. If not provided, the current OS is used.
        arch: The target CPU architecture. If not provided, the
            current architecture is used.

    Returns:
        The resolved target.

    Raises:
        ValueError: if ``python_version`` ends with ``t`` and
            ``free_threaded=False`` is specified.

    Example:
        ```pycon
        >>> from feu.compat.target import resolve_target
        >>> resolve_target(python_version="3.14t", os="linux", arch="x86_64")
        Target(python_version='3.14', free_threaded=True, os='linux', arch='x86_64')

        ```
    """
    python_version = python_version or get_python_version()
    if python_version.endswith("t"):
        if free_threaded is False:
            msg = (
                f"python_version '{python_version}' indicates a free-threaded build but "
                "free_threaded=False was specified"
            )
            raise ValueError(msg)
        python_version = python_version[:-1]
        free_threaded = True
    if free_threaded is None:
        free_threaded = is_free_threaded()
    return Target(
        python_version=python_version,
        free_threaded=free_threaded,
        os=os or get_current_os(),
        arch=arch or get_current_arch(),
    )
