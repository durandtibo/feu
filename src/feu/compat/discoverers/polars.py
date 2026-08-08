r"""Define the ``polars`` compatibility discoverer."""

from __future__ import annotations

__all__ = ["PolarsCompatDiscoverer"]

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

POLARS_RUNTIME_PKG_NAME = "polars-runtime-32"


class PolarsCompatDiscoverer(BaseCompatDiscoverer):
    r"""Implement a specialized compatibility discoverer for ``polars``.

    Older ``polars`` releases ship platform-specific compiled wheels
    directly, so the default ``CompatDiscoverer`` logic (matching
    wheel tags exactly) works fine for those. Starting with ``polars``
    1.34, however, the ``polars`` wheel itself became pure-Python and
    delegates the compiled, platform-specific parts to the separate
    ``polars-runtime-32`` package, pinned to an exact version per
    release. The default discoverer cannot see this indirection: it
    falls back to the ``requires_python`` metadata for pure-Python
    wheels and (incorrectly) considers every such ``polars`` release
    compatible with every OS/arch/free-threaded combination.

    This discoverer handles both eras correctly: it matches wheel tags
    directly for releases that ship platform-specific wheels, and for
    pure-Python releases it resolves the pinned ``polars-runtime-32``
    version and matches against that release's wheel tags instead.

    Example:
        ```pycon
        >>> from feu.compat.discoverers.polars import PolarsCompatDiscoverer
        >>> from feu.compat.target import Target
        >>> discoverer = PolarsCompatDiscoverer()
        >>> compat = discoverer.discover(
        ...     "polars", targets=(Target(python_version="3.11", os="linux", arch="x86_64"),)
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
        runtime_tags_by_version: dict[str, set[WheelTags]] | None = None

        runtime_tags: dict[str, set[WheelTags]] = {}
        for version, tags in tags_by_version.items():
            if any(tag.python_version is not None for tag in tags):
                continue
            runtime_version = fetch_pypi_pinned_dependency_version(
                pkg_name, version, POLARS_RUNTIME_PKG_NAME
            )
            if runtime_version is None:
                continue
            if runtime_tags_by_version is None:
                runtime_tags_by_version = build_tags_by_version(
                    fetch_pypi_wheel_filenames(POLARS_RUNTIME_PKG_NAME)
                )
            runtime_tags[version] = runtime_tags_by_version.get(runtime_version, set())

        def _is_version_compatible(version: str, _target: Target, wanted: WheelTags) -> bool:
            return _is_target_compatible(
                wanted, tags_by_version[version], runtime_tags.get(version)
            )

        return build_compat_ranges(versions, latest, targets, _is_version_compatible)


def _is_target_compatible(
    wanted: WheelTags, tags: set[WheelTags], runtime_tags: set[WheelTags] | None
) -> bool:
    r"""Indicate if a ``polars`` release satisfies a wanted target.

    A release that ships platform-specific wheels must match the
    target's Python version, free-threaded, OS, and arch axes exactly. A
    release that only ships a pure-Python wheel is compatible only if
    its pinned ``polars-runtime-32`` release shipped a wheel matching
    those axes exactly.
    """
    for tag in tags:
        if tag.python_version is None:
            if runtime_tags is None:
                continue
            if any(tags_match_exactly(runtime_tag, wanted) for runtime_tag in runtime_tags):
                return True
            continue
        if tags_match_exactly(tag, wanted):
            return True
    return False
