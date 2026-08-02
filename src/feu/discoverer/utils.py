r"""Define helper functions shared by compatibility discoverers."""

from __future__ import annotations

__all__ = [
    "build_tags_by_version",
    "sort_stable_versions",
    "tags_match_exactly",
    "target_to_wheel_tags",
    "versions_to_ranges",
]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.compat.registry import VersionRange
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.version import filter_stable_versions, filter_valid_versions

if TYPE_CHECKING:
    from collections.abc import Iterable

    from feu.compat.target import Target


def sort_stable_versions(versions: Iterable[str]) -> list[str]:
    r"""Filter and sort the stable, valid versions from a collection of
    version strings.

    Args:
        versions: The version strings to filter and sort, e.g. the
            keys of a package's wheel filenames mapping.

    Returns:
        The stable, valid versions, sorted in ascending order.
    """
    return sorted(filter_stable_versions(filter_valid_versions(versions)), key=Version)


def build_tags_by_version(
    wheel_filenames: dict[str, tuple[str, ...]],
) -> dict[str, set[WheelTags]]:
    r"""Build a mapping of version to the wheel tags parsed from its
    published wheel filenames.

    Args:
        wheel_filenames: Mapping of version to published wheel
            filenames for that version.

    Returns:
        A mapping of version to the set of ``WheelTags`` parsed from
            that version's wheel filenames.
    """
    return {
        version: {tags for filename in filenames for tags in parse_wheel_filename(filename)}
        for version, filenames in wheel_filenames.items()
    }


def target_to_wheel_tags(target: Target) -> WheelTags:
    r"""Convert a compatibility target to the ``WheelTags`` it is looking
    for.

    Args:
        target: The compatibility target.

    Returns:
        The ``WheelTags`` matching the target's Python
            version/free-threaded/OS/arch axes.
    """
    return WheelTags(
        python_version=target.python_version,
        free_threaded=target.free_threaded,
        os=target.os,
        arch=target.arch,
    )


def tags_match_exactly(tag: WheelTags, wanted: WheelTags) -> bool:
    r"""Indicate if a wheel tag matches a wanted target exactly.

    A match requires the Python version, free-threaded, OS, and arch
    axes to all agree.

    Args:
        tag: The wheel tag to check.
        wanted: The tags describing the wanted target.

    Returns:
        ``True`` if the tag matches the wanted target exactly.
    """
    return (
        tag.python_version == wanted.python_version
        and tag.free_threaded == wanted.free_threaded
        and tag.os == wanted.os
        and tag.arch == wanted.arch
    )


def versions_to_ranges(compatible: list[str], latest: str | None) -> list[VersionRange]:
    r"""Convert a list of compatible versions to a list of
    ``VersionRange``.

    Args:
        compatible: The versions found compatible with a target,
            sorted in ascending order.
        latest: The latest known stable version of the package, or
            ``None`` if unknown. Used to leave the upper bound open
            when the compatible range extends to the latest version.

    Returns:
        An empty list if ``compatible`` is empty, otherwise a
            single-element list containing the ``VersionRange``
            spanning the compatible versions.
    """
    if not compatible:
        return []
    return [VersionRange(compatible[0], None if compatible[-1] == latest else compatible[-1])]
