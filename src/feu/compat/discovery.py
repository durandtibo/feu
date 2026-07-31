r"""Contain functions to automatically discover package/Python-version
compatibility constraints from PyPI metadata."""

from __future__ import annotations

__all__ = [
    "DEFAULT_PYTHON_VERSIONS",
    "DEFAULT_TARGETS",
    "discover_compat",
    "discover_compat_targets",
]

from typing import TYPE_CHECKING

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

from feu.compat.registry import UNSUPPORTED
from feu.compat.target import Target
from feu.compat.wheel_tags import WheelTags, parse_wheel_filename
from feu.version.filtering import filter_stable_versions, filter_valid_versions
from feu.version.pypi import fetch_pypi_requires_python, fetch_pypi_wheel_filenames

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_PYTHON_VERSIONS = ("3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15")


def discover_compat(
    pkg_name: str, python_versions: Sequence[str] = DEFAULT_PYTHON_VERSIONS
) -> dict[str, dict[str, str | None]]:
    r"""Discover the min/max package version compatible with each Python
    version, using the ``requires_python`` metadata published on PyPI.

    For each Python version, ``min`` is set to the earliest stable
    package release compatible with it, and ``max`` is set to the
    latest compatible release, or ``None`` if the newest stable
    release overall is still compatible (i.e. no upper bound has been
    hit yet). If no stable release is compatible with a given Python
    version, both ``min`` and ``max`` are set to
    ``feu.compat.registry.UNSUPPORTED``.

    Args:
        pkg_name: The package name to inspect (e.g., ``"numpy"``).
        python_versions: The Python versions to compute constraints
            for. Defaults to ``DEFAULT_PYTHON_VERSIONS``.

    Returns:
        A mapping of Python version to ``{"min": ..., "max": ...}``,
            in the same shape expected by ``CompatRegistry.register_many``.

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

    result: dict[str, dict[str, str | None]] = {}
    for python_version in python_versions:
        compatible = [
            version
            for version in versions
            if _is_compatible(requires_python[version], python_version)
        ]
        if not compatible:
            result[python_version] = {"min": UNSUPPORTED, "max": UNSUPPORTED}
            continue
        result[python_version] = {
            "min": compatible[0],
            "max": None if compatible[-1] == latest else compatible[-1],
        }
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


DEFAULT_TARGETS: tuple[Target, ...] = tuple(
    Target(python_version=python_version, free_threaded=free_threaded, os=os, arch=arch)
    for python_version in DEFAULT_PYTHON_VERSIONS
    for free_threaded in (False, True)
    for os in ("linux", "macos", "windows")
    for arch in ("x86_64", "arm64")
)


def discover_compat_targets(
    pkg_name: str, targets: Sequence[Target] = DEFAULT_TARGETS
) -> dict[Target, dict[str, str | None]]:
    r"""Discover the min/max package version compatible with each
    target, using actual wheel filenames published on PyPI.

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
        A mapping of ``Target`` to ``{"min": ..., "max": ...}``, in
            the same shape expected by
            ``CompatRegistry.register_many``.

    Example:
        ```pycon
        >>> from feu.compat.discovery import discover_compat_targets
        >>> compat = discover_compat_targets("numpy")  # doctest: +SKIP

        ```
    """
    wheel_filenames = fetch_pypi_wheel_filenames(pkg_name)
    versions = filter_stable_versions(filter_valid_versions(wheel_filenames.keys()))
    versions = sorted(versions, key=Version)
    latest = versions[-1] if versions else None

    tags_by_version: dict[str, set[WheelTags]] = {
        version: {
            tags
            for filename in wheel_filenames[version]
            if (tags := parse_wheel_filename(filename)) is not None
        }
        for version in versions
    }

    result: dict[Target, dict[str, str | None]] = {}
    for target in targets:
        wanted = WheelTags(
            python_version=target.python_version,
            free_threaded=target.free_threaded,
            os=target.os,
            arch=target.arch,
        )
        compatible = [version for version in versions if wanted in tags_by_version[version]]
        if not compatible:
            result[target] = {"min": UNSUPPORTED, "max": UNSUPPORTED}
            continue
        result[target] = {
            "min": compatible[0],
            "max": None if compatible[-1] == latest else compatible[-1],
        }
    return result
