r"""Define the ``duckdb`` compatibility discoverer."""

from __future__ import annotations

__all__ = ["DuckdbCompatDiscoverer"]

from typing import TYPE_CHECKING

from feu.compat.discoverers.base import BaseCompatDiscoverer
from feu.compat.discoverers.default import discover_from_wheel_filenames
from feu.version import fetch_pypi_wheel_filenames

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.registry import VersionRange
    from feu.compat.target import Target

IGNORED_VERSIONS = frozenset({"0.0.0"})


class DuckdbCompatDiscoverer(BaseCompatDiscoverer):
    r"""Implement a specialized compatibility discoverer for ``duckdb``.

    ``duckdb`` has a spurious ``0.0.0`` release published on PyPI in
    2023. It is not a real release, and including it in version
    ordering only creates confusion in the computed compatibility
    ranges. This discoverer behaves exactly like the default
    ``CompatDiscoverer`` but ignores that version.

    Example:
        ```pycon
        >>> from feu.compat.discoverers.duckdb import DuckdbCompatDiscoverer
        >>> from feu.compat.target import Target
        >>> discoverer = DuckdbCompatDiscoverer()
        >>> compat = discoverer.discover(
        ...     "duckdb", targets=(Target(python_version="3.11", os="linux", arch="x86_64"),)
        ... )  # doctest: +SKIP

        ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def discover(
        self, pkg_name: str, targets: Sequence[Target]
    ) -> dict[Target, list[VersionRange]]:
        wheel_filenames = fetch_pypi_wheel_filenames(pkg_name)
        wheel_filenames = {
            version: filenames
            for version, filenames in wheel_filenames.items()
            if version not in IGNORED_VERSIONS
        }
        return discover_from_wheel_filenames(pkg_name, targets, wheel_filenames)
