r"""Contain the function that discovers the package/target compatibility
from the files published on PyPI.

One algorithm is used for every package. The packages whose wheels do
not carry the platform tags themselves are described by data (a
*companion* package, a version to ignore), not by a class.
"""

from __future__ import annotations

__all__ = [
    "COMPANIONS",
    "IGNORED_VERSIONS",
    "Companion",
    "Discovery",
    "PinnedDependency",
    "SameVersion",
    "discover_compat_targets",
    "group_into_ranges",
    "is_compatible",
    "tags_match_exactly",
]

from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import Version

from feu.compat.registry import VersionRange
from feu.compat.target import DEFAULT_TARGETS
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.version import (
    fetch_pypi_pinned_dependency_version,
    fetch_pypi_requires_python,
    fetch_pypi_wheel_filenames,
    filter_stable_versions,
    filter_valid_versions,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Mapping, Sequence

    from feu.compat.target import Target


@dataclass(frozen=True)
class SameVersion:
    r"""Describe a companion package that has a release with the same
    version (e.g. ``jax`` and ``jaxlib``).

    Args:
        package: The companion package name.
    """

    package: str


@dataclass(frozen=True)
class PinnedDependency:
    r"""Describe a companion package whose release is pinned by the
    release of the package (e.g. ``polars`` pins ``polars-runtime-32``
    and ``pydantic`` pins ``pydantic-core``).

    Args:
        package: The companion package name.
    """

    package: str


Companion = SameVersion | PinnedDependency

#: The packages whose platform wheels are published by a companion package.
COMPANIONS: dict[str, Companion] = {
    "jax": SameVersion("jaxlib"),
    "polars": PinnedDependency("polars-runtime-32"),
    "pydantic": PinnedDependency("pydantic-core"),
}

#: The releases to ignore, by canonical package name.
IGNORED_VERSIONS: dict[str, frozenset[str]] = {"duckdb": frozenset({"0.0.0"})}


class Discovery(NamedTuple):
    r"""Represent the result of ``discover_compat_targets``.

    Args:
        versions: The releases that were considered (stable, valid and
            not ignored), in PEP 440 order.
        targets: The ranges of compatible versions of each target. A
            range that reaches the latest release is open (its
            ``max`` is ``None``).
    """

    versions: tuple[str, ...]
    targets: dict[Target, list[VersionRange]]


def is_compatible(requires_python: str | None, python_version: str) -> bool:
    r"""Indicate if a ``requires_python`` specifier allows a given Python
    version.

    Args:
        requires_python: The ``requires_python`` specifier string, or
            ``None`` if the release does not declare one.
        python_version: The Python version to check (e.g., ``"3.11"``).

    Returns:
        ``True`` if the release is compatible or declares no
            constraint (or an invalid one), ``False`` otherwise.

    Example:
        ```pycon
        >>> from feu.compat import is_compatible
        >>> is_compatible(">=3.9", "3.11")
        True
        >>> is_compatible(">=3.9", "3.8")
        False

        ```
    """
    if not requires_python:
        return True
    try:
        return SpecifierSet(requires_python).contains(python_version, prereleases=True)
    except InvalidSpecifier:
        return True


def tags_match_exactly(tag: WheelTags, wanted: WheelTags) -> bool:
    r"""Indicate if a wheel tag runs on a wanted platform.

    The ``os``, ``arch`` and ``free_threaded`` fields must be equal. An
    ``abi3`` wheel matches a Python version at or above its own; any
    other wheel needs the same Python version. A pure-Python tag (its
    ``os`` and ``arch`` are ``None``) never matches a platform.

    Args:
        tag: The tag of a wheel.
        wanted: The wanted platform.

    Returns:
        ``True`` if the wheel runs on the wanted platform.

    Example:
        ```pycon
        >>> from feu.compat.wheel_tags import WheelTags
        >>> from feu.compat import tags_match_exactly
        >>> tag = WheelTags("3.9", False, "linux", "x86_64", abi3=True)
        >>> tags_match_exactly(tag, WheelTags("3.12", False, "linux", "x86_64"))
        True

        ```
    """
    if tag.os != wanted.os or tag.arch != wanted.arch or tag.free_threaded != wanted.free_threaded:
        return False
    if tag.abi3:
        return (
            tag.python_version is not None
            and wanted.python_version is not None
            and Version(wanted.python_version) >= Version(tag.python_version)
        )
    return tag.python_version == wanted.python_version


def _is_tag_compatible(tag: WheelTags, wanted: WheelTags, requires_python: str | None) -> bool:
    r"""Indicate if a wheel tag of a package without companion is
    compatible with a wanted platform.

    Args:
        tag: The tag of a wheel.
        wanted: The wanted platform.
        requires_python: The ``requires-python`` of the release.

    Returns:
        ``True`` if the wheel is compatible. A pure-Python wheel is
            compatible with every platform when ``requires_python``
            allows the wanted Python version.
    """
    if tag.os is not None and tag.os != wanted.os:
        return False
    if tag.arch is not None and tag.arch != wanted.arch:
        return False
    if tag.python_version is None:
        return wanted.python_version is not None and is_compatible(
            requires_python, wanted.python_version
        )
    if tag.free_threaded != wanted.free_threaded:
        return False
    if tag.abi3:
        return wanted.python_version is not None and Version(wanted.python_version) >= Version(
            tag.python_version
        )
    return tag.python_version == wanted.python_version


def group_into_ranges(
    versions: Sequence[str], compatible: Collection[str], latest: str | None
) -> list[VersionRange]:
    r"""Group the compatible versions into ranges of consecutive
    releases.

    Args:
        versions: All the considered versions, in ascending order.
        compatible: The versions that are compatible.
        latest: The latest release. A range that ends with it is open.

    Returns:
        The ranges of consecutive compatible versions. The ``max`` of a
            range that reaches ``latest`` is ``None``.

    Example:
        ```pycon
        >>> from feu.compat import group_into_ranges
        >>> group_into_ranges(["1", "2", "3", "4"], {"1", "2", "4"}, "4")
        [VersionRange(min='1', max='2'), VersionRange(min='4', max=None)]

        ```
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


def _tags_by_version(
    wheel_filenames: Mapping[str, tuple[str, ...]],
) -> dict[str, set[WheelTags]]:
    r"""Parse the wheel file names of each release.

    Args:
        wheel_filenames: The wheel file names of each release.

    Returns:
        The tags of each release.
    """
    return {
        version: {tag for filename in filenames for tag in parse_wheel_filename(filename)}
        for version, filenames in wheel_filenames.items()
    }


def _companion_tags(
    pkg_name: str,
    companion: Companion,
    version: str,
    companion_tags: dict[str, set[WheelTags]] | None,
) -> set[WheelTags]:
    r"""Get the tags of the companion release of a release.

    Args:
        pkg_name: The package name.
        companion: The companion of the package.
        version: The release of the package.
        companion_tags: The tags of each release of the companion
            package.

    Returns:
        The tags of the companion release. The set is empty if the
            companion release is unknown.
    """
    if companion_tags is None:
        return set()
    if isinstance(companion, SameVersion):
        return companion_tags.get(version, set())
    pinned = fetch_pypi_pinned_dependency_version(pkg_name, version, companion.package)
    return companion_tags.get(pinned, set()) if pinned is not None else set()


def _default_judge(
    pkg_name: str, tags: Mapping[str, set[WheelTags]]
) -> Callable[[str, WheelTags], bool]:
    r"""Create the compatibility check of a package without companion.

    Args:
        pkg_name: The package name.
        tags: The tags of each considered release.

    Returns:
        A function that indicates if a release is compatible with a
            wanted platform.
    """
    has_pure_python_wheel = any(tag.python_version is None for t in tags.values() for tag in t)
    requires_python = fetch_pypi_requires_python(pkg_name) if has_pure_python_wheel else {}

    def judge(version: str, wanted: WheelTags) -> bool:
        python_requirement = requires_python.get(version)
        if not tags[version]:
            # A release without wheel is treated as pure Python only if some release
            # of the package published a pure-Python wheel.
            return (
                has_pure_python_wheel
                and wanted.python_version is not None
                and is_compatible(python_requirement, wanted.python_version)
            )
        return any(_is_tag_compatible(tag, wanted, python_requirement) for tag in tags[version])

    return judge


def _companion_judge(
    pkg_name: str, companion: Companion, tags: Mapping[str, set[WheelTags]]
) -> Callable[[str, WheelTags], bool]:
    r"""Create the compatibility check of a package with a companion.

    Args:
        pkg_name: The package name.
        companion: The companion of the package.
        tags: The tags of each considered release.

    Returns:
        A function that indicates if a release is compatible with a
            wanted platform.
    """
    companion_tags: dict[str, set[WheelTags]] | None = None
    effective: dict[str, set[WheelTags]] = {}
    for version, version_tags in tags.items():
        # A pure-Python wheel of the package says nothing about the platform.
        platform_tags = {tag for tag in version_tags if tag.python_version is not None}
        if platform_tags:
            effective[version] = platform_tags
            continue
        if companion_tags is None:
            companion_tags = _tags_by_version(fetch_pypi_wheel_filenames(companion.package))
        effective[version] = _companion_tags(pkg_name, companion, version, companion_tags)

    def judge(version: str, wanted: WheelTags) -> bool:
        return any(tags_match_exactly(tag, wanted) for tag in effective[version])

    return judge


def _sorted_stable_versions(versions: Collection[str], ignored: Collection[str]) -> list[str]:
    r"""Keep the stable, valid and not ignored versions, in PEP 440
    order.

    Args:
        versions: The versions.
        ignored: The versions to ignore.

    Returns:
        The kept versions in ascending order.
    """
    kept = filter_stable_versions(filter_valid_versions(versions))
    return sorted((v for v in kept if v not in ignored), key=Version)


def discover_compat_targets(
    pkg_name: str,
    targets: Sequence[Target] = DEFAULT_TARGETS,
    *,
    companion: Companion | None = None,
    ignore_versions: Collection[str] | None = None,
) -> Discovery:
    r"""Discover the versions of a package that are compatible with each
    target, from the files published on PyPI.

    A release is compatible with a target if a wheel runs on it:

    - A package **without** companion: one wheel matches exactly
      (Python version, free-threaded flag, OS and architecture), or is
      ``abi3`` with a minimum Python at or below the target, or is
      pure Python and ``requires-python`` allows the target. A release
      with **no** wheel is treated as pure Python only if some release
      of the package published a pure-Python wheel.
    - A package **with** a companion (``jax``, ``polars``,
      ``pydantic``): a pure-Python wheel of the package says nothing
      about the platform and never counts. The release is judged by its
      platform wheels if it has any; otherwise by the wheels of the
      companion release (the release with the same version, or the one
      pinned by the release). An unknown companion release means
      "not compatible".

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        targets: The compatibility targets to compute constraints for.
            Each target must have concrete (non-``None``) ``os`` and
            ``arch``. Defaults to ``DEFAULT_TARGETS``.
        companion: The companion package. ``None`` means the one
            registered for the package in ``COMPANIONS``, if any.
        ignore_versions: The releases to ignore. ``None`` means the
            ones registered for the package in ``IGNORED_VERSIONS``.

    Returns:
        The considered versions and the ranges of compatible versions
            of each target. The ranges can be given to
            ``CompatRegistry.register_many``.

    Example:
        ```pycon
        >>> from feu.compat import discover_compat_targets
        >>> discovery = discover_compat_targets("numpy")  # doctest: +SKIP

        ```
    """
    name = canonicalize_name(pkg_name)
    if companion is None:
        companion = COMPANIONS.get(name)
    ignored = (
        IGNORED_VERSIONS.get(name, frozenset()) if ignore_versions is None else ignore_versions
    )

    wheel_filenames = fetch_pypi_wheel_filenames(pkg_name)
    versions = _sorted_stable_versions(wheel_filenames.keys(), ignored)
    latest = versions[-1] if versions else None
    tags = _tags_by_version({version: wheel_filenames[version] for version in versions})

    if companion is None:
        compatible_with = _default_judge(pkg_name, tags)
    else:
        compatible_with = _companion_judge(pkg_name, companion, tags)

    result: dict[Target, list[VersionRange]] = {}
    for target in targets:
        wanted = WheelTags(
            python_version=target.python_version,
            free_threaded=target.free_threaded,
            os=target.os,
            arch=target.arch,
        )
        compatible = {version for version in versions if compatible_with(version, wanted)}
        result[target] = group_into_ranges(versions, compatible, latest)
    return Discovery(versions=tuple(versions), targets=result)
