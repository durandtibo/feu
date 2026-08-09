r"""Contain functions to automatically discover package/Python-version
compatibility constraints from PyPI metadata."""

from __future__ import annotations

__all__ = [
    "DEFAULT_PYTHON_VERSIONS",
    "DEFAULT_TARGETS",
    "is_compatible",
    "show_compat_targets",
]

from typing import TYPE_CHECKING

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

from feu.compat.target import Target
from feu.imports import check_rich, is_rich_available

if TYPE_CHECKING:
    from feu.compat.registry import VersionRange

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


def is_compatible(requires_python: str | None, python_version: str) -> bool:
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
    table.add_column("Versions")

    for target, ranges in compat.items():
        table.add_row(
            target.python_version,
            str(target.free_threaded),
            target.os or "-",
            target.arch or "-",
            _format_ranges(ranges),
        )

    get_console().print(table)


def _format_ranges(ranges: list[VersionRange]) -> str:
    r"""Format a list of ``VersionRange`` as a single display string.

    Args:
        ranges: The version ranges to format. An empty list means no
            version is valid for the target.

    Returns:
        A comma-separated ``"min - max"`` string for each range, or
            ``"unsupported"`` if ``ranges`` is empty.
    """
    if not ranges:
        return "[red]unsupported[/red]"
    return ", ".join(
        f"{version_range.min or '-'} - {version_range.max or '[green]latest[/green]'}"
        for version_range in ranges
    )
