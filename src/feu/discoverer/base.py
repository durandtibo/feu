r"""Define the compatibility discoverer base class."""

from __future__ import annotations

__all__ = ["BaseCompatDiscoverer", "group_into_ranges"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from feu.compat.registry import VersionRange

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.target import Target


class BaseCompatDiscoverer(ABC):
    r"""Define the base class for package compatibility target
    discoverers.

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

    @abstractmethod
    def discover(
        self, pkg_name: str, targets: Sequence[Target]
    ) -> dict[Target, list[VersionRange]]:
        r"""Discover the version range compatible with each target.

        Args:
            pkg_name: The package name to inspect (e.g., ``"numpy"``).
            targets: The compatibility targets to compute constraints
                for. Each target must have concrete (non-``None``)
                ``os`` and ``arch``.

        Returns:
            A mapping of ``Target`` to a list of ``VersionRange``, in
                the same shape expected by
                ``CompatRegistry.register_many``.
        """


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
