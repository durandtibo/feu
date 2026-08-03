r"""Contain functions to parse PEP 427 wheel filenames into
compatibility-relevant tags."""

from __future__ import annotations

__all__ = [
    "ARCH_TABLE",
    "OS_TABLE",
    "WheelTags",
    "parse_arch",
    "parse_os",
    "parse_pure_python_tag",
    "parse_python_tag",
    "parse_wheel_filename",
]

import re
from dataclasses import dataclass

_PYTHON_TAG_PATTERN = re.compile(r"^cp3(\d+)$")
_PURE_PYTHON_TAG_COMPONENT_PATTERN = re.compile(r"^py(\d)(\d*)$")

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
        python_version: The CPython version, e.g. ``"3.14"``, or
            ``None`` for a pure-Python wheel compatible with any
            Python version. For an ``abi3`` wheel, this is the
            *minimum* CPython version it supports, since the stable
            ABI makes it forward-compatible with later versions too.
        free_threaded: ``True`` if the wheel targets a free-threaded
            (no-GIL) build.
        os: The operating system, e.g. ``"linux"``, ``"macos"``,
            ``"windows"``, or ``None`` for a pure-Python wheel
            compatible with any OS.
        arch: The CPU architecture, e.g. ``"x86_64"``, ``"arm64"``, or
            ``None`` for a pure-Python wheel compatible with any
            architecture.
        abi3: ``True`` if the wheel targets the CPython stable ABI
            (an ``abi3`` ABI tag), meaning it is forward-compatible
            with every CPython version from ``python_version`` onward,
            not just that exact version.
    """

    python_version: str | None
    free_threaded: bool
    os: str | None
    arch: str | None
    abi3: bool = False


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


def parse_pure_python_tag(python_tag: str) -> list[str | None] | None:
    r"""Parse a wheel Python tag into the pure-Python versions it
    targets.

    A bare major tag (e.g. ``"py3"``) carries no minor version, so it
    is compatible with any minor version of that major and is
    represented as ``None`` (a wildcard). A tag with an explicit minor
    (e.g. ``"py36"``) targets that exact Python version only, like a
    CPython tag. A compressed, dot-separated tag (e.g.
    ``"py2.py3"`` or ``"py35.py36"``) yields one entry per component.

    Args:
        python_tag: The wheel Python tag, e.g. ``"py3"`` or
            ``"py35.py36"``.

    Returns:
        A list with one entry per dot-separated component (``None``
            for a wildcard major-only component, or a version string
            such as ``"3.6"`` for a major.minor component), or
            ``None`` if any component doesn't match the ``py<digits>``
            pattern.

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import parse_pure_python_tag
        >>> parse_pure_python_tag("py3")
        [None]
        >>> parse_pure_python_tag("py36")
        ['3.6']

        ```
    """
    versions: list[str | None] = []
    for component in python_tag.split("."):
        match = _PURE_PYTHON_TAG_COMPONENT_PATTERN.match(component)
        if not match:
            return None
        major, minor = match.groups()
        versions.append(f"{major}.{minor}" if minor else None)
    return versions


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


def parse_wheel_filename(filename: str) -> list[WheelTags]:
    r"""Parse a PEP 427 wheel filename into compatibility tags.

    Args:
        filename: The wheel filename, e.g.
            ``"numpy-2.3.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"``.

    Returns:
        A list of ``WheelTags``, one per Python-tag component (more
            than one only for a compressed pure-Python tag such as
            ``"py2.py3"``), or an empty list if the filename doesn't
            end in ``.whl``, targets a non-CPython/non-pure-Python
            interpreter, or its platform tag isn't in the known
            ``os``/``arch`` tables (and isn't the universal ``"any"``
            platform). A bare major pure-Python component (e.g.
            ``"py3"``) yields ``python_version=None`` (compatible with
            any minor version), while a major.minor component (e.g.
            ``"py36"``) yields an exact version like a CPython tag.
            The universal ``"any"`` platform tag yields ``os=None``
            and ``arch=None``, meaning "compatible with any".

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import parse_wheel_filename
        >>> parse_wheel_filename("numpy-2.3.0-cp312-cp312-macosx_11_0_arm64.whl")
        [WheelTags(python_version='3.12', free_threaded=False, os='macos', arch='arm64')]

        ```
    """
    if not filename.endswith(".whl"):
        return []
    stem = filename[: -len(".whl")]
    parts = stem.split("-")
    if len(parts) < 5:
        return []
    python_tag, abi_tag, platform_tag = parts[-3], parts[-2], parts[-1]

    cpython_version = parse_python_tag(python_tag)
    if cpython_version is not None:
        python_versions: list[str | None] = [cpython_version]
    else:
        pure_python_versions = parse_pure_python_tag(python_tag)
        if pure_python_versions is None:
            return []
        python_versions = pure_python_versions

    first_platform_component = platform_tag.split(".")[0]
    if first_platform_component == "any":
        os_name = None
        arch_name = None
    else:
        os_name = parse_os(first_platform_component)
        arch_name = parse_arch(first_platform_component)
        if os_name is None or arch_name is None:
            return []

    free_threaded = abi_tag.endswith("t")
    abi3 = abi_tag == "abi3"

    return [
        WheelTags(
            python_version=python_version,
            free_threaded=free_threaded,
            os=os_name,
            arch=arch_name,
            abi3=abi3,
        )
        for python_version in python_versions
    ]
