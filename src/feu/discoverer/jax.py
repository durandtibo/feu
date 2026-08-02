r"""Define the ``jax`` compatibility discoverer."""

from __future__ import annotations

__all__ = ["JaxCompatDiscoverer"]

from typing import TYPE_CHECKING

from feu.discoverer.base import BaseCompatDiscoverer
from feu.discoverer.utils import (
    build_tags_by_version,
    sort_stable_versions,
    tags_match_exactly,
    target_to_wheel_tags,
    versions_to_ranges,
)
from feu.version import fetch_pypi_wheel_filenames

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.registry import VersionRange
    from feu.compat.target import Target
    from feu.compat.wheel_tags import WheelTags

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
        jax_versions = sort_stable_versions(fetch_pypi_wheel_filenames(pkg_name).keys())
        latest = jax_versions[-1] if jax_versions else None

        jaxlib_tags_by_version = build_tags_by_version(fetch_pypi_wheel_filenames(JAXLIB_PKG_NAME))

        result: dict[Target, list[VersionRange]] = {}
        for target in targets:
            wanted = target_to_wheel_tags(target)
            compatible = [
                version
                for version in jax_versions
                if _is_target_compatible(wanted, jaxlib_tags_by_version.get(version, set()))
            ]
            result[target] = versions_to_ranges(compatible, latest)
        return result


def _is_target_compatible(wanted: WheelTags, tags: set[WheelTags]) -> bool:
    r"""Indicate if a ``jaxlib`` release's wheels satisfy a wanted
    target.

    Unlike pure-Python packages, ``jaxlib`` always ships platform-
    specific wheels, so a match requires the Python version, free-
    threaded, OS, and arch axes to all agree exactly.
    """
    return any(tags_match_exactly(tag, wanted) for tag in tags)
