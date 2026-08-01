r"""Contain functions to automatically discover package/Python-version
compatibility constraints from PyPI metadata."""

from __future__ import annotations

__all__ = [
    "DEFAULT_PYTHON_VERSIONS",
    "DEFAULT_TARGETS",
    "discover_compat",
    "discover_compat_targets",
    "show_compat_targets",
]

from typing import TYPE_CHECKING

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

from feu.compat.registry import VersionRange
from feu.compat.target import Target
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.imports import check_rich, is_rich_available
from feu.version import (
    fetch_pypi_requires_python,
    fetch_pypi_wheel_filenames,
    filter_stable_versions,
    filter_valid_versions,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

if is_rich_available():  # pragma: no cover
    from rich import get_console
    from rich.table import Table


DEFAULT_PYTHON_VERSIONS = ("3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15")

DEFAULT_TARGETS: tuple[Target, ...] = tuple(
    Target(python_version=python_version, free_threaded=free_threaded, os=os, arch=arch)
    for python_version in DEFAULT_PYTHON_VERSIONS
    for free_threaded in ((False, True) if Version(python_version) >= Version("3.13") else (False,))
    for os in ("linux", "macos", "windows")
    for arch in ("x86_64", "arm64")
)


def discover_compat(
    pkg_name: str, python_versions: Sequence[str] = DEFAULT_PYTHON_VERSIONS
) -> dict[str, list[VersionRange]]:
    r"""Discover the version range compatible with each Python version,
    using the ``requires_python`` metadata published on PyPI.

    For each Python version, the earliest stable package release
    compatible with it becomes the range's ``min``, and the latest
    compatible release becomes its ``max``, or ``None`` if the newest
    stable release overall is still compatible (i.e. no upper bound
    has been hit yet). If no stable release is compatible with a
    given Python version, the range list is empty.

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        python_versions: The Python versions to compute constraints
            for. Defaults to ``DEFAULT_PYTHON_VERSIONS``.

    Returns:
        A mapping of Python version to a list of ``VersionRange``, in
            the same shape expected by ``CompatRegistry.register_many``.

    Example:
        ```pycon
        >>> from feu.compat import discover_compat
        >>> compat = discover_compat("requests")  # doctest: +SKIP

        ```
    """
    requires_python = fetch_pypi_requires_python(pkg_name)
    versions = filter_stable_versions(filter_valid_versions(requires_python.keys()))
    versions = sorted(versions, key=Version)
    latest = versions[-1] if versions else None

    result: dict[str, list[VersionRange]] = {}
    for python_version in python_versions:
        compatible = [
            version
            for version in versions
            if _is_compatible(requires_python[version], python_version)
        ]
        if not compatible:
            result[python_version] = []
            continue
        result[python_version] = [
            VersionRange(compatible[0], None if compatible[-1] == latest else compatible[-1])
        ]
    return result


def _is_compatible(requires_python: str | None, python_version: str) -> bool:
    r"""Indicate if a ``requires_python`` specifier allows a given Python
    version.

    Args:
        requires_python: The ``requires_python`` specifier string, or
            ``None`` if the release does not declare one.
        python_version: The Python version to check (e.g., ``"3.11"``).

    Returns:
        ``True`` if the release is compatible or declares no
            constraint, ``False`` otherwise.
    """
    if not requires_python:
        return True
    try:
        return SpecifierSet(requires_python).contains(python_version, prereleases=True)
    except InvalidSpecifier:
        return True


def discover_compat_targets(
    pkg_name: str, targets: Sequence[Target] = DEFAULT_TARGETS
) -> dict[Target, list[VersionRange]]:
    r"""Discover the version range compatible with each target, using
    actual wheel filenames published on PyPI.

    Unlike ``discover_compat``, which only inspects the
    ``requires_python`` metadata, this function parses each release's
    wheel filenames to determine whether it shipped a build matching
    a target's free-threaded/OS/arch axes, not just its Python
    version.

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        targets: The compatibility targets to compute constraints for.
            Each target must have concrete (non-``None``) ``os`` and
            ``arch``. Defaults to ``DEFAULT_TARGETS``.

    Returns:
        A mapping of ``Target`` to a list of ``VersionRange``, in the
            same shape expected by ``CompatRegistry.register_many``.

    Example:
        ```pycon
        >>> from feu.compat import discover_compat_targets
        >>> compat = discover_compat_targets("numpy")  # doctest: +SKIP

        ```
    """
    wheel_filenames = fetch_pypi_wheel_filenames(pkg_name)
    versions = filter_stable_versions(filter_valid_versions(wheel_filenames.keys()))
    versions = sorted(versions, key=Version)
    latest = versions[-1] if versions else None

    tags_by_version: dict[str, set[WheelTags]] = {
        version: {
            tags for filename in wheel_filenames[version] for tags in parse_wheel_filename(filename)
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
            if _is_compatible(requires_python, wanted_python_version):
                return True
            continue
        if tag.python_version != wanted.python_version:
            continue
        if tag.free_threaded != wanted.free_threaded:
            continue
        return True
    return False


def show_compat_targets(
    compat: dict[Target, list[VersionRange]], pkg_name: str | None = None
) -> None:
    r"""Print the output of ``discover_compat_targets`` as a table.

    Args:
        compat: The mapping of ``Target`` to a list of ``VersionRange``,
            as returned by ``discover_compat_targets``.
        pkg_name: The package name to show in the table title, if any.

    Raises:
        RuntimeError: if the ``rich`` package is not installed.

    Example:
        ```pycon
        >>> from feu.compat import discover_compat_targets, show_compat_targets
        >>> compat = discover_compat_targets("numpy")  # doctest: +SKIP
        >>> show_compat_targets(compat, pkg_name="numpy")  # doctest: +SKIP

        ```
    """
    check_rich()

    table = Table(title=f"Compatibility for {pkg_name}" if pkg_name else "Compatibility")
    table.add_column("Python")
    table.add_column("Free-threaded")
    table.add_column("OS")
    table.add_column("Arch")
    table.add_column("Min version")
    table.add_column("Max version")

    for target, ranges in compat.items():
        if not ranges:
            table.add_row(
                target.python_version,
                str(target.free_threaded),
                target.os or "-",
                target.arch or "-",
                "[red]unsupported[/red]",
                "[red]unsupported[/red]",
            )
            continue
        for version_range in ranges:
            table.add_row(
                target.python_version,
                str(target.free_threaded),
                target.os or "-",
                target.arch or "-",
                version_range.min or "-",
                version_range.max or "[green]latest[/green]",
            )

    get_console().print(table)
