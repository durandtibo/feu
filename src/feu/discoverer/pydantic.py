r"""Define the ``pydantic`` compatibility discoverer."""

from __future__ import annotations

__all__ = ["PydanticCompatDiscoverer"]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.discoverer.base import BaseCompatDiscoverer, group_into_ranges
from feu.version import (
    fetch_pypi_pinned_dependency_version,
    fetch_pypi_wheel_filenames,
    filter_stable_versions,
    filter_valid_versions,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.registry import VersionRange
    from feu.compat.target import Target

PYDANTIC_CORE_PKG_NAME = "pydantic-core"


class PydanticCompatDiscoverer(BaseCompatDiscoverer):
    r"""Implement a specialized compatibility discoverer for
    ``pydantic``.

    ``pydantic`` 1.x ships platform-specific compiled wheels directly,
    so the default ``CompatDiscoverer`` logic (matching wheel tags
    exactly) works fine for those releases. ``pydantic`` 2.x, however,
    ships a pure-Python wheel and delegates the compiled, platform-
    specific parts to the separate ``pydantic-core`` package, pinned
    to an exact version per release. The default discoverer cannot see
    this indirection: it falls back to the ``requires_python``
    metadata for pure-Python wheels and (incorrectly) considers every
    ``pydantic`` 2.x release compatible with every OS/arch/free-
    threaded combination.

    This discoverer handles both eras correctly: it matches wheel tags
    directly for releases that ship platform-specific wheels, and for
    pure-Python releases it resolves the pinned ``pydantic-core``
    version and matches against that release's wheel tags instead.

    Example:
        ```pycon
        >>> from feu.discoverer.pydantic import PydanticCompatDiscoverer
        >>> from feu.compat.target import Target
        >>> discoverer = PydanticCompatDiscoverer()
        >>> compat = discoverer.discover(
        ...     "pydantic", targets=(Target(python_version="3.11", os="linux", arch="x86_64"),)
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

        core_tags_by_version: dict[str, set[WheelTags]] = {}
        for version, tags in tags_by_version.items():
            if any(tag.python_version is not None for tag in tags):
                continue
            core_version = fetch_pypi_pinned_dependency_version(
                pkg_name, version, PYDANTIC_CORE_PKG_NAME
            )
            if core_version is None:
                continue
            core_tags_by_version[version] = _fetch_tags(PYDANTIC_CORE_PKG_NAME, core_version)

        result: dict[Target, list[VersionRange]] = {}
        for target in targets:
            wanted = WheelTags(
                python_version=target.python_version,
                free_threaded=target.free_threaded,
                os=target.os,
                arch=target.arch,
            )
            compatible = {
                version
                for version in versions
                if _is_target_compatible(
                    wanted, tags_by_version[version], core_tags_by_version.get(version)
                )
            }
            result[target] = group_into_ranges(versions, compatible, latest)
        return result


def _fetch_tags(pkg_name: str, version: str) -> set[WheelTags]:
    r"""Fetch the wheel tags published for a single release of a
    package."""
    filenames = fetch_pypi_wheel_filenames(pkg_name).get(version, ())
    return {tags for filename in filenames for tags in parse_wheel_filename(filename)}


def _is_target_compatible(
    wanted: WheelTags, tags: set[WheelTags], core_tags: set[WheelTags] | None
) -> bool:
    r"""Indicate if a ``pydantic`` release satisfies a wanted target.

    A release that ships platform-specific wheels (``pydantic`` 1.x)
    must match the target's Python version, free-threaded, OS, and arch
    axes exactly. A release that only ships a pure-Python wheel
    (``pydantic`` 2.x) is compatible only if its pinned ``pydantic-
    core`` release shipped a wheel matching those axes exactly.
    """
    for tag in tags:
        if tag.python_version is None:
            if core_tags is None:
                continue
            for core_tag in core_tags:
                if core_tag.python_version != wanted.python_version:
                    continue
                if core_tag.free_threaded != wanted.free_threaded:
                    continue
                if core_tag.os != wanted.os:
                    continue
                if core_tag.arch != wanted.arch:
                    continue
                return True
            continue
        if tag.python_version != wanted.python_version:
            continue
        if tag.free_threaded != wanted.free_threaded:
            continue
        if tag.os != wanted.os:
            continue
        if tag.arch != wanted.arch:
            continue
        return True
    return False
