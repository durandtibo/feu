r"""Define the default compatibility discoverer."""

from __future__ import annotations

__all__ = ["CompatDiscoverer"]

from typing import TYPE_CHECKING

from packaging.version import Version

from feu.compat.discovery import is_compatible
from feu.discoverer.base import BaseCompatDiscoverer
from feu.discoverer.utils import build_compat_ranges, build_tags_by_version
from feu.version import (
    fetch_pypi_requires_python,
    fetch_pypi_wheel_filenames,
    filter_stable_versions,
    filter_valid_versions,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.registry import VersionRange
    from feu.compat.target import Target
    from feu.compat.wheel_tags import WheelTags


class CompatDiscoverer(BaseCompatDiscoverer):
    r"""Implement the default compatibility target discoverer, using
    actual wheel filenames published on PyPI.

    Unlike an approach that only inspects the ``requires_python``
    metadata, this discoverer parses each release's wheel filenames to
    determine whether it shipped a build matching a target's
    free-threaded/OS/arch axes, not just its Python version. For
    pure-Python wheels (which carry no OS/arch information, and
    sometimes no Python-version information either), it falls back to
    the ``requires_python`` metadata.

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
        return discover_from_wheel_filenames(
            pkg_name, targets, fetch_pypi_wheel_filenames(pkg_name)
        )


def discover_from_wheel_filenames(
    pkg_name: str,
    targets: Sequence[Target],
    wheel_filenames: dict[str, tuple[str, ...]],
) -> dict[Target, list[VersionRange]]:
    r"""Compute the compatibility target ranges from a pre-fetched
    mapping of version to wheel filenames.

    This is the implementation used by ``CompatDiscoverer.discover``,
    extracted so specialized discoverers (e.g. ``DuckdbCompatDiscoverer``)
    can reuse the wheel-tag-based matching logic on a filtered/adjusted
    set of wheel filenames.

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        targets: The compatibility targets to compute constraints for.
        wheel_filenames: Mapping of version to published wheel
            filenames for that version.

    Returns:
        A mapping of ``Target`` to a list of ``VersionRange``, in the
            same shape expected by ``CompatRegistry.register_many``.
    """
    versions = filter_stable_versions(filter_valid_versions(wheel_filenames.keys()))
    versions = sorted(versions, key=Version)
    latest = versions[-1] if versions else None

    tags_by_version = build_tags_by_version(
        {version: wheel_filenames[version] for version in versions}
    )
    has_pure_python_wheel = any(
        tag.python_version is None for tags in tags_by_version.values() for tag in tags
    )
    requires_python = fetch_pypi_requires_python(pkg_name) if has_pure_python_wheel else {}

    def _is_version_compatible(version: str, target: Target, wanted: WheelTags) -> bool:
        return _is_target_compatible(
            wanted,
            target.python_version,
            tags_by_version[version],
            requires_python.get(version),
            treat_sdist_as_pure_python=has_pure_python_wheel,
        )

    return build_compat_ranges(versions, latest, targets, _is_version_compatible)


def _is_target_compatible(
    wanted: WheelTags,
    wanted_python_version: str,
    tags: set[WheelTags],
    requires_python: str | None,
    treat_sdist_as_pure_python: bool = False,
) -> bool:
    r"""Indicate if a release's wheels satisfy a wanted target.

    A release is compatible if it shipped a wheel matching the
    target's Python version, OS, arch, and free-threaded axes
    exactly, or a pure-Python wheel (``python_version``/``os``/
    ``arch`` of ``None``, meaning "any") whose ``requires_python``
    metadata allows the target's Python version. Pure-Python wheels
    are assumed compatible with any OS/arch and both free-threaded and
    standard builds.

    A release with no wheel files at all (e.g. sdist-only) is treated
    the same way, falling back to ``requires_python``, but only when
    ``treat_sdist_as_pure_python`` is ``True`` -- i.e. the package has
    published pure-Python wheels for at least one other release. That
    signal indicates the package has no compiled/ABI dependencies, so
    a missing wheel for a given release is most likely a packaging
    accident rather than evidence of a compiled extension whose
    buildability for the target can't be verified. Without that
    signal (e.g. a package that only ever ships platform-specific
    wheels, such as numpy), a missing wheel is treated as
    incompatible, since an sdist build isn't proof the release
    supports the target's OS/arch/free-threading.

    Args:
        wanted: The tags describing the wanted target.
        wanted_python_version: The wanted target's Python version.
        tags: The wheel tags parsed from the release's wheel
            filenames.
        requires_python: The release's ``requires_python`` specifier,
            used only to validate pure-Python and sdist-only releases.
        treat_sdist_as_pure_python: If ``True``, a release with no
            wheel files falls back to ``requires_python`` instead of
            being treated as incompatible.

    Returns:
        ``True`` if the release satisfies the wanted target.
    """
    if not tags:
        return treat_sdist_as_pure_python and is_compatible(requires_python, wanted_python_version)
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
