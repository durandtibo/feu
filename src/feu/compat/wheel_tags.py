r"""Contain functions to parse PEP 427 wheel filenames into
compatibility-relevant tags."""

from __future__ import annotations

__all__ = [
    "ARCH_TABLE",
    "OS_TABLE",
    "WheelTags",
    "parse_arch",
    "parse_os",
    "parse_python_tag",
    "parse_wheel_filename",
]

import re
from dataclasses import dataclass

_PYTHON_TAG_PATTERN = re.compile(r"^cp3(\d+)$")

OS_TABLE: dict[str, str] = {
    "manylinux": "linux",
    "linux": "linux",
    "macosx": "macos",
    "win_amd64": "windows",
    "win_arm64": "windows",
    "win32": "windows",
}

ARCH_TABLE: dict[str, str] = {
    "x86_64": "x86_64",
    "amd64": "x86_64",
    "aarch64": "arm64",
    "arm64": "arm64",
}


@dataclass(frozen=True)
class WheelTags:
    r"""Compatibility-relevant tags extracted from a wheel filename.

    Args:
        python_version: The CPython version, e.g. ``"3.14"``.
        free_threaded: ``True`` if the wheel targets a free-threaded
            (no-GIL) build.
        os: The operating system, e.g. ``"linux"``, ``"macos"``,
            ``"windows"``.
        arch: The CPU architecture, e.g. ``"x86_64"``, ``"arm64"``.
    """

    python_version: str
    free_threaded: bool
    os: str
    arch: str


def parse_python_tag(python_tag: str) -> str | None:
    r"""Parse a wheel Python tag into a CPython version string.

    Args:
        python_tag: The wheel Python tag, e.g. ``"cp312"``.

    Returns:
        The CPython version, e.g. ``"3.12"``, or ``None`` if the tag
            doesn't match a CPython 3.x tag (e.g. ``"py3"``,
            ``"pp310"``).

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import parse_python_tag
        >>> parse_python_tag("cp312")
        '3.12'

        ```
    """
    match = _PYTHON_TAG_PATTERN.match(python_tag)
    if not match:
        return None
    digits = match.group(1)
    return f"3.{digits}"


def parse_os(platform_tag: str) -> str | None:
    r"""Parse the operating system from a wheel platform tag.

    Args:
        platform_tag: The first dot-separated component of the wheel
            platform tag, e.g. ``"manylinux_2_17_x86_64"``.

    Returns:
        The operating system name, e.g. ``"linux"``, ``"macos"``,
            ``"windows"``, or ``None`` if the tag doesn't match any
            known prefix in ``OS_TABLE``.

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import parse_os
        >>> parse_os("manylinux_2_17_x86_64")
        'linux'

        ```
    """
    for key, os_name in OS_TABLE.items():
        if platform_tag.startswith(key):
            return os_name
    return None


def parse_arch(platform_tag: str) -> str | None:
    r"""Parse the CPU architecture from a wheel platform tag.

    Args:
        platform_tag: The first dot-separated component of the wheel
            platform tag, e.g. ``"manylinux_2_17_x86_64"``.

    Returns:
        The architecture name, e.g. ``"x86_64"``, ``"arm64"``, or
            ``None`` if the tag doesn't contain any known substring in
            ``ARCH_TABLE``.

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import parse_arch
        >>> parse_arch("manylinux_2_17_x86_64")
        'x86_64'

        ```
    """
    for key, arch_name in ARCH_TABLE.items():
        if key in platform_tag:
            return arch_name
    return None


def parse_wheel_filename(filename: str) -> WheelTags | None:
    r"""Parse a PEP 427 wheel filename into compatibility tags.

    Args:
        filename: The wheel filename, e.g.
            ``"numpy-2.3.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"``.

    Returns:
        The parsed ``WheelTags``, or ``None`` if the filename doesn't
            end in ``.whl``, targets a non-CPython interpreter, or its
            platform tag isn't in the known ``os``/``arch`` tables.

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import parse_wheel_filename
        >>> parse_wheel_filename("numpy-2.3.0-cp312-cp312-macosx_11_0_arm64.whl")
        WheelTags(python_version='3.12', free_threaded=False, os='macos', arch='arm64')

        ```
    """
    if not filename.endswith(".whl"):
        return None
    stem = filename[: -len(".whl")]
    parts = stem.split("-")
    if len(parts) < 5:
        return None
    python_tag, abi_tag, platform_tag = parts[-3], parts[-2], parts[-1]

    python_version = parse_python_tag(python_tag)
    if python_version is None:
        return None

    first_platform_component = platform_tag.split(".")[0]
    os_name = parse_os(first_platform_component)
    arch_name = parse_arch(first_platform_component)
    if os_name is None or arch_name is None:
        return None

    free_threaded = abi_tag.endswith("t")

    return WheelTags(
        python_version=python_version, free_threaded=free_threaded, os=os_name, arch=arch_name
    )
