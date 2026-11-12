r"""Contain the parser of the tags of a wheel file name.

The file name is parsed by ``packaging.utils.parse_wheel_filename``,
which expands the compressed tag sets (e.g.
``macosx_10_9_x86_64.macosx_11_0_arm64``). Each ``(interpreter, abi,
platform)`` is then mapped to a ``WheelTag``.

The platforms that ``feu`` knows are ``linux``, ``macos`` and
``windows`` on ``x86_64`` and ``arm64`` (the vocabulary of ``Target``).
The other platforms (``musllinux``, ``win32``, ``i686``, ``armv7l``,
``ppc64le``, ...) and the other interpreters (PyPy, GraalPy, ...) are
**out of scope**: they give no tag.
"""

from __future__ import annotations

__all__ = ["WheelTag", "parse_wheel_filename"]

import re
from dataclasses import dataclass

from packaging.utils import InvalidWheelFilename, parse_wheel_filename as _parse_wheel_filename

_CPYTHON_PATTERN = re.compile(r"cp3(\d+)")
_PURE_PYTHON_PATTERN = re.compile(r"py\d+")
_FREE_THREADED_ABI_PATTERN = re.compile(r"cp3\d+t|abi3t")
_ABI3_PATTERN = re.compile(r"abi3t?")
_MACOS_PATTERN = re.compile(r"macosx_\d+_\d+_(x86_64|arm64|universal2)")
_LINUX_PATTERN = re.compile(r"(?:many|)linux(?:_\d+_\d+|\d+)?_(x86_64|aarch64)")

_Platform = tuple[str | None, str | None]
_FIXED_PLATFORMS: dict[str, tuple[_Platform, ...]] = {
    "any": ((None, None),),
    "win_amd64": (("windows", "x86_64"),),
    "win_arm64": (("windows", "arm64"),),
}


@dataclass(frozen=True)
class WheelTag:
    r"""Represent one ``(interpreter, abi, platform)`` tag of a wheel.

    Args:
        python_version: The CPython version (e.g. ``"3.12"``) or the
            minimum CPython version of a stable-ABI wheel. ``None``
            for a pure-Python (``py3``) wheel.
        free_threaded: ``True`` for a free-threaded build
            (``cp313t`` and ``abi3t``).
        os: The operating system (``"linux"``, ``"macos"`` or
            ``"windows"``), or ``None`` for a wheel that runs on any
            platform.
        arch: The CPU architecture (``"x86_64"`` or ``"arm64"``), or
            ``None`` for a wheel that runs on any platform.
        abi3: ``True`` for a stable-ABI wheel (``abi3`` and ``abi3t``),
            which runs on its Python version and the later ones.

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import WheelTag
        >>> WheelTag(python_version="3.12", free_threaded=False, os="linux", arch="x86_64")
        WheelTag(python_version='3.12', free_threaded=False, os='linux', arch='x86_64', abi3=False)

        ```
    """

    python_version: str | None
    free_threaded: bool
    os: str | None
    arch: str | None
    abi3: bool = False


def _parse_platform(platform_tag: str) -> tuple[_Platform, ...]:
    r"""Map a platform tag to ``(os, arch)`` pairs.

    Args:
        platform_tag: The platform tag, e.g. ``"manylinux_2_17_x86_64"``.

    Returns:
        The ``(os, arch)`` pairs. A ``macosx_*_universal2`` wheel runs
            on both architectures. The tuple is empty for a platform
            that is out of scope. ``any`` gives ``(None, None)``.
    """
    if platform_tag in _FIXED_PLATFORMS:
        return _FIXED_PLATFORMS[platform_tag]
    if match := _MACOS_PATTERN.fullmatch(platform_tag):
        arch = match.group(1)
        if arch == "universal2":
            return (("macos", "x86_64"), ("macos", "arm64"))
        return (("macos", arch),)
    if match := _LINUX_PATTERN.fullmatch(platform_tag):
        return (("linux", "arm64" if match.group(1) == "aarch64" else "x86_64"),)
    return ()


def _parse_python(interpreter: str) -> tuple[bool, str | None]:
    r"""Map an interpreter tag to a Python version.

    Args:
        interpreter: The interpreter tag, e.g. ``"cp312"`` or ``"py3"``.

    Returns:
        A pair ``(in_scope, python_version)``. ``in_scope`` is
            ``False`` for an interpreter other than CPython and
            pure Python. The version is ``None`` for pure Python.
    """
    if match := _CPYTHON_PATTERN.fullmatch(interpreter):
        return True, f"3.{match.group(1)}"
    if _PURE_PYTHON_PATTERN.fullmatch(interpreter):
        return True, None
    return False, None


def parse_wheel_filename(filename: str) -> tuple[WheelTag, ...]:
    r"""Parse the tags of a wheel file name.

    Args:
        filename: The wheel file name, e.g.
            ``"numpy-2.3.0-cp312-cp312-manylinux_2_17_x86_64.whl"``.

    Returns:
        The distinct tags of the wheel, sorted. A wheel with a
            compressed tag set (``macosx_10_9_x86_64.macosx_11_0_arm64``)
            or a ``universal2`` wheel gives one tag per platform. The
            tuple is empty if ``filename`` is not a valid wheel file
            name, or if every tag is out of scope (``musllinux``,
            ``win32``, ``i686``, PyPy, ...).

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import parse_wheel_filename
        >>> parse_wheel_filename("numpy-2.3.0-cp312-cp312-macosx_11_0_universal2.whl")
        (WheelTag(python_version='3.12', free_threaded=False, os='macos', arch='arm64', abi3=False),
         WheelTag(python_version='3.12', free_threaded=False, os='macos', arch='x86_64', abi3=False))

        ```
    """
    try:
        tags = _parse_wheel_filename(filename)[3]
    except InvalidWheelFilename:
        return ()
    result: set[WheelTag] = set()
    for tag in tags:
        in_scope, python_version = _parse_python(tag.interpreter)
        if not in_scope:
            continue
        free_threaded = _FREE_THREADED_ABI_PATTERN.fullmatch(tag.abi) is not None
        abi3 = _ABI3_PATTERN.fullmatch(tag.abi) is not None
        if abi3 and python_version is None:
            continue
        result.update(
            WheelTag(
                python_version=python_version,
                free_threaded=free_threaded,
                os=os,
                arch=arch,
                abi3=abi3,
            )
            for os, arch in _parse_platform(tag.platform)
        )
    return tuple(
        sorted(
            result,
            key=lambda t: (
                t.python_version or "",
                t.free_threaded,
                t.os or "",
                t.arch or "",
                t.abi3,
            ),
        )
    )
