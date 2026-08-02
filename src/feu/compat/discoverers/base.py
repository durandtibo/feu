r"""Define the compatibility discoverer base class."""

from __future__ import annotations

__all__ = ["BaseCompatDiscoverer"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from feu.compat.registry import VersionRange
    from feu.compat.target import Target


class BaseCompatDiscoverer(ABC):
    r"""Define the base class for package compatibility target
    discoverers.

    Example:
        ```pycon
        >>> from feu.compat.discoverers import CompatDiscoverer
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
