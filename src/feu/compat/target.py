r"""Define the compatibility target key used to look up package version
constraints."""

from __future__ import annotations

__all__ = [
    "DEFAULT_TARGETS",
    "PLATFORMS",
    "PYTHON_VERSIONS",
    "VALID_ARCH",
    "VALID_OS",
    "Target",
    "resolve_target",
]

import re
from dataclasses import dataclass

from packaging.version import Version

from feu.utils.platform import (
    get_current_arch,
    get_current_os,
    get_python_version,
    is_free_threaded,
)

_PYTHON_VERSION_PATTERN = re.compile(r"\d+\.\d+")
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
        if not _PYTHON_VERSION_PATTERN.fullmatch(self.python_version):
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
    python_version: str | None = None, *, free_threaded: bool | None = None
) -> Target:
    r"""Resolve the ``Target`` of an environment.

    The platform (OS and CPU architecture) is always the current one.
    The Python version and the free-threaded flag can be chosen, e.g.
    by a CI matrix that checks other Python versions, and fall back to
    the current interpreter.

    If ``python_version`` ends with ``t``, the target is a
    free-threaded build. In that case, ``free_threaded=False`` is
    invalid because it contradicts the ``t`` suffix.

    Args:
        python_version: The Python version, e.g. ``"3.11"`` or
            ``"3.14t"``. If not provided, the current python version
            is used.
        free_threaded: Whether the target is a free-threaded build.
            If not provided, it is inferred from ``python_version`` or
            the current interpreter's free-threaded status.

    Returns:
        The resolved target, with the current OS and architecture.

    Raises:
        ValueError: if ``python_version`` ends with ``t`` and
            ``free_threaded=False`` is specified.

    Example:
        ```pycon
        >>> from feu.compat.target import resolve_target
        >>> target = resolve_target(python_version="3.14t")
        >>> target.python_version, target.free_threaded
        ('3.14', True)

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
        os=get_current_os(),
        arch=get_current_arch(),
    )


#: The Python versions of the shipped compatibility data.
PYTHON_VERSIONS = ("3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15")

#: The ``(os, arch)`` platforms of the shipped compatibility data.
PLATFORMS: tuple[tuple[str, str], ...] = tuple(
    (os, arch) for os in ("linux", "macos", "windows") for arch in ("x86_64", "arm64")
)

#: The targets of the shipped compatibility data: every Python version, with and
#: without free-threading from Python 3.13, and every platform.
DEFAULT_TARGETS: tuple[Target, ...] = tuple(
    Target(python_version=python_version, free_threaded=free_threaded, os=os, arch=arch)
    for python_version in PYTHON_VERSIONS
    for free_threaded in ((False, True) if Version(python_version) >= Version("3.13") else (False,))
    for os, arch in PLATFORMS
)
