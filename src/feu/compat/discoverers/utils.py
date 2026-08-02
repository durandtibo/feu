r"""Define helper functions shared by compatibility discoverers."""

from __future__ import annotations

__all__ = [
    "build_compat_ranges",
    "build_tags_by_version",
    "group_into_ranges",
    "sort_stable_versions",
    "tags_match_exactly",
    "target_to_wheel_tags",
]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.compat.registry import VersionRange
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.version import filter_stable_versions, filter_valid_versions

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

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


def group_into_ranges(
    versions: Sequence[str], compatible: set[str], latest: str | None
) -> list[VersionRange]:
    r"""Group a set of compatible versions into contiguous
    ``VersionRange`` objects, following the sorted ``versions`` order.

    Compatibility is not guaranteed to be contiguous across a
    package's version history (e.g. an old release gaining a backport
    wheel for a new Python version while intermediate releases never
    did, or a release accidentally dropping a platform wheel), so runs
    of compatible versions must be tracked individually instead of
    collapsed into a single min/max span.

    Args:
        versions: All the versions considered, sorted ascending.
        compatible: The subset of ``versions`` that satisfy a target.
        latest: The overall latest version, or ``None`` if
            ``versions`` is empty. The final range's ``max`` is
            ``None`` (unbounded) when its end is ``latest``.

    Returns:
        The list of contiguous ``VersionRange`` objects covering
            ``compatible``.
    """
    ranges: list[VersionRange] = []
    run_start: str | None = None
    run_end: str | None = None
    for version in versions:
        if version in compatible:
            if run_start is None:
                run_start = version
            run_end = version
        elif run_start is not None:
            ranges.append(VersionRange(run_start, run_end))
            run_start = None
    if run_start is not None:
        ranges.append(VersionRange(run_start, None if run_end == latest else run_end))
    return ranges


def build_compat_ranges(
    versions: Sequence[str],
    latest: str | None,
    targets: Sequence[Target],
    is_version_compatible: Callable[[str, Target, WheelTags], bool],
) -> dict[Target, list[VersionRange]]:
    r"""Build the per-target compatibility ranges from a version
    compatibility predicate.

    Args:
        versions: All the versions considered, sorted ascending.
        latest: The overall latest version, or ``None`` if
            ``versions`` is empty.
        targets: The compatibility targets to compute constraints for.
        is_version_compatible: Callable indicating if a given version
            is compatible with a given target, called with the
            version, the target, and the target's ``WheelTags``.

    Returns:
        A mapping of ``Target`` to a list of ``VersionRange``, in the
            same shape expected by ``CompatRegistry.register_many``.
    """
    result: dict[Target, list[VersionRange]] = {}
    for target in targets:
        wanted = target_to_wheel_tags(target)
        compatible = {
            version for version in versions if is_version_compatible(version, target, wanted)
        }
        result[target] = group_into_ranges(versions, compatible, latest)
    return result
