r"""Define the ``pydantic`` compatibility discoverer."""

from __future__ import annotations

__all__ = ["PydanticCompatDiscoverer"]

from typing import TYPE_CHECKING

from feu.compat.discoverers.base import BaseCompatDiscoverer
from feu.compat.discoverers.utils import (
    build_compat_ranges,
    build_tags_by_version,
    sort_stable_versions,
    tags_match_exactly,
)
from feu.version import fetch_pypi_pinned_dependency_version, fetch_pypi_wheel_filenames

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.registry import VersionRange
    from feu.compat.target import Target
    from feu.compat.wheel_tags import WheelTags

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
        >>> from feu.compat.discoverers.pydantic import PydanticCompatDiscoverer
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
        versions = sort_stable_versions(wheel_filenames.keys())
        latest = versions[-1] if versions else None

        tags_by_version = build_tags_by_version(
            {version: wheel_filenames[version] for version in versions}
        )
        pydantic_core_tags_by_version: dict[str, set[WheelTags]] | None = None

        core_tags_by_version: dict[str, set[WheelTags]] = {}
        for version, tags in tags_by_version.items():
            if any(tag.python_version is not None for tag in tags):
                continue
            core_version = fetch_pypi_pinned_dependency_version(
                pkg_name, version, PYDANTIC_CORE_PKG_NAME
            )
            if core_version is None:
                continue
            if pydantic_core_tags_by_version is None:
                pydantic_core_tags_by_version = build_tags_by_version(
                    fetch_pypi_wheel_filenames(PYDANTIC_CORE_PKG_NAME)
                )
            core_tags_by_version[version] = pydantic_core_tags_by_version.get(core_version, set())

        def _is_version_compatible(version: str, _target: Target, wanted: WheelTags) -> bool:
            return _is_target_compatible(
                wanted, tags_by_version[version], core_tags_by_version.get(version)
            )

        return build_compat_ranges(versions, latest, targets, _is_version_compatible)


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
            if any(tags_match_exactly(core_tag, wanted) for core_tag in core_tags):
                return True
            continue
        if tags_match_exactly(tag, wanted):
            return True
    return False
