r"""Define the default compatibility discoverer."""

from __future__ import annotations

__all__ = ["CompatDiscoverer"]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.compat.discovery import is_compatible
from feu.compat.registry import VersionRange
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.discoverer.base import BaseCompatDiscoverer
from feu.version import (
    fetch_pypi_requires_python,
    fetch_pypi_wheel_filenames,
    filter_stable_versions,
    filter_valid_versions,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.target import Target


class CompatDiscoverer(BaseCompatDiscoverer):
    r"""Implement the default compatibility target discoverer, using
    actual wheel filenames published on PyPI.

    Unlike ``discover_compat``, which only inspects the
    ``requires_python`` metadata, this discoverer parses each
    release's wheel filenames to determine whether it shipped a build
    matching a target's free-threaded/OS/arch axes, not just its
    Python version. For pure-Python wheels (which carry no OS/arch
    information, and sometimes no Python-version information either),
    it falls back to the ``requires_python`` metadata.

    Example:
        ```pycon
        >>> from feu.compat.discoverer import CompatDiscoverer
        >>> from feu.compat.target import Target
        >>> discoverer = CompatDiscoverer()
        >>> compat = discoverer.discover(
        ...     "numpy", targets=(Target(python_version="3.11", os="linux", arch="x86_64"),)
        ... )  # doctest: +SKIP

        ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def discover(
        self, pkg_name: str, targets: Sequence[Target]
    ) -> dict[Target, list[VersionRange]]:
        wheel_filenames = fetch_pypi_wheel_filenames(pkg_name)
        versions = filter_stable_versions(filter_valid_versions(wheel_filenames.keys()))
        versions = sorted(versions, key=Version)
        latest = versions[-1] if versions else None

        tags_by_version: dict[str, set[WheelTags]] = {
            version: {
                tags
                for filename in wheel_filenames[version]
                for tags in parse_wheel_filename(filename)
            }
            for version in versions
        }
        has_pure_python_wheel = any(
            tag.python_version is None for tags in tags_by_version.values() for tag in tags
        )
        requires_python = fetch_pypi_requires_python(pkg_name) if has_pure_python_wheel else {}

        result: dict[Target, list[VersionRange]] = {}
        for target in targets:
            wanted = WheelTags(
                python_version=target.python_version,
                free_threaded=target.free_threaded,
                os=target.os,
                arch=target.arch,
            )
            compatible = [
                version
                for version in versions
                if _is_target_compatible(
                    wanted,
                    target.python_version,
                    tags_by_version[version],
                    requires_python.get(version),
                )
            ]
            if not compatible:
                result[target] = []
                continue
            result[target] = [
                VersionRange(compatible[0], None if compatible[-1] == latest else compatible[-1])
            ]
        return result


def _is_target_compatible(
    wanted: WheelTags,
    wanted_python_version: str,
    tags: set[WheelTags],
    requires_python: str | None,
) -> bool:
    r"""Indicate if a release's wheels satisfy a wanted target.

    A release is compatible if it shipped a wheel matching the
    target's Python version, OS, arch, and free-threaded axes
    exactly, or a pure-Python wheel (``python_version``/``os``/
    ``arch`` of ``None``, meaning "any") whose ``requires_python``
    metadata allows the target's Python version. Pure-Python wheels
    are assumed compatible with any OS/arch and both free-threaded and
    standard builds.

    Args:
        wanted: The tags describing the wanted target.
        wanted_python_version: The wanted target's Python version.
        tags: The wheel tags parsed from the release's wheel
            filenames.
        requires_python: The release's ``requires_python`` specifier,
            used only to validate pure-Python wheels.

    Returns:
        ``True`` if the release satisfies the wanted target.
    """
    for tag in tags:
        if tag.os is not None and tag.os != wanted.os:
            continue
        if tag.arch is not None and tag.arch != wanted.arch:
            continue
        if tag.python_version is None:
            if is_compatible(requires_python, wanted_python_version):
                return True
            continue
        if tag.python_version != wanted.python_version:
            continue
        if tag.free_threaded != wanted.free_threaded:
            continue
        return True
    return False
