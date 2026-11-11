r"""Contain functions to display the discovered compatibility."""

from __future__ import annotations

__all__ = ["show_compat_targets"]

from typing import TYPE_CHECKING

from feu.compat.discover import Discovery
from feu.imports import check_rich

if TYPE_CHECKING:
    from collections.abc import Mapping

    from feu.compat.registry import VersionRange
    from feu.compat.target import Target


def show_compat_targets(
    compat: Discovery | Mapping[Target, list[VersionRange]], pkg_name: str | None = None
) -> None:
    r"""Print the output of ``discover_compat_targets`` as a table.

    Args:
        compat: The output of ``discover_compat_targets``, or a mapping
            of ``Target`` to a list of ``VersionRange``.
        pkg_name: The package name to show in the table title, if any.

    Raises:
        MissingPackageError: if the ``rich`` package is not installed.

    Example:
        ```pycon
        >>> from feu.compat import discover_compat_targets, show_compat_targets
        >>> compat = discover_compat_targets("numpy")  # doctest: +SKIP
        >>> show_compat_targets(compat, pkg_name="numpy")  # doctest: +SKIP

        ```
    """
    check_rich()
    from rich import get_console  # noqa: PLC0415
    from rich.table import Table  # noqa: PLC0415

    table = Table(title=f"Compatibility for {pkg_name}" if pkg_name else "Compatibility")
    table.add_column("Python")
    table.add_column("Free-threaded")
    table.add_column("OS")
    table.add_column("Arch")
    table.add_column("Versions")

    targets = compat.targets if isinstance(compat, Discovery) else compat
    for target, ranges in targets.items():
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
