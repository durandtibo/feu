r"""Define the ``jax`` compatibility discoverer."""

from __future__ import annotations

__all__ = ["JaxCompatDiscoverer"]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.discoverer.base import BaseCompatDiscoverer, group_into_ranges
from feu.version import (
    fetch_pypi_wheel_filenames,
    filter_stable_versions,
    filter_valid_versions,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.registry import VersionRange
    from feu.compat.target import Target

JAXLIB_PKG_NAME = "jaxlib"


class JaxCompatDiscoverer(BaseCompatDiscoverer):
    r"""Implement a specialized compatibility discoverer for ``jax``.

    ``jax`` itself ships pure-Python wheels, so its own wheel
    filenames carry no OS/arch/Python-version information: the
    default ``CompatDiscoverer`` would (incorrectly) consider every
    ``jax`` release compatible with every target. In practice, ``jax``
    requires ``jaxlib``, whose wheels are platform-specific and are
    released in lockstep with matching ``jax`` version numbers. This
    discoverer therefore only considers a ``jax`` release compatible
    with a target if the ``jaxlib`` release with the same version
    number shipped a wheel matching that target's Python
    version/free-threaded/OS/arch axes.

    Example:
        ```pycon
        >>> from feu.discoverer.jax import JaxCompatDiscoverer
        >>> from feu.compat.target import Target
        >>> discoverer = JaxCompatDiscoverer()
        >>> compat = discoverer.discover(
        ...     "jax", targets=(Target(python_version="3.11", os="linux", arch="x86_64"),)
        ... )  # doctest: +SKIP

        ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def discover(
        self, pkg_name: str, targets: Sequence[Target]
    ) -> dict[Target, list[VersionRange]]:
        jax_versions = _fetch_sorted_stable_versions(pkg_name)
        latest = jax_versions[-1] if jax_versions else None

        jaxlib_tags_by_version = _fetch_tags_by_version(JAXLIB_PKG_NAME)

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
                for version in jax_versions
                if _is_target_compatible(wanted, jaxlib_tags_by_version.get(version, set()))
            }
            result[target] = group_into_ranges(jax_versions, compatible, latest)
        return result


def _fetch_sorted_stable_versions(pkg_name: str) -> list[str]:
    r"""Fetch and sort the stable release versions of a package."""
    wheel_filenames = fetch_pypi_wheel_filenames(pkg_name)
    versions = filter_stable_versions(filter_valid_versions(wheel_filenames.keys()))
    return sorted(versions, key=Version)


def _fetch_tags_by_version(pkg_name: str) -> dict[str, set[WheelTags]]:
    r"""Fetch the wheel tags published for each release of a package."""
    wheel_filenames = fetch_pypi_wheel_filenames(pkg_name)
    return {
        version: {tags for filename in filenames for tags in parse_wheel_filename(filename)}
        for version, filenames in wheel_filenames.items()
    }


def _is_target_compatible(wanted: WheelTags, tags: set[WheelTags]) -> bool:
    r"""Indicate if a ``jaxlib`` release's wheels satisfy a wanted
    target.

    Unlike pure-Python packages, ``jaxlib`` always ships platform-
    specific wheels, so a match requires the Python version, free-
    threaded, OS, and arch axes to all agree exactly.
    """
    for tag in tags:
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
