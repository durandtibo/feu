r"""Define the compatibility registry for package version resolution.

This module provides a registry system that manages and resolves valid
package version ranges per compatibility target, enabling lookup of the
closest valid version and validation of a given version.
"""

from __future__ import annotations

__all__ = ["CompatRegistry", "UnsupportedVersionError", "VersionRange"]

import copy
from typing import TYPE_CHECKING, NamedTuple

from packaging.version import Version

if TYPE_CHECKING:
    from feu.compat.target import Target


class VersionRange(NamedTuple):
    r"""Represent one contiguous range of valid package versions.

    Args:
        min: The minimum valid package version, or ``None`` for no
            minimum.
        max: The maximum valid package version, or ``None`` for no
            maximum.
    """

    min: str | None
    max: str | None


class UnsupportedVersionError(Exception):
    r"""Raised when no package version is compatible with a given
    target."""


class CompatRegistry:
    r"""Manage package version compatibility across different
    compatibility targets.

    The registry maps package name to ``Target`` to a list of
    ``VersionRange``. A package version is valid for a target if it
    falls within any of the registered ranges; an empty list means no
    version is valid for that target. A lookup target matches a
    stored entry when ``python_version`` and ``free_threaded`` are
    equal, and the stored entry's ``os``/``arch`` are either ``None``
    (wildcard) or equal to the lookup target's ``os``/``arch``. Among
    all matching entries, the most specific one (most non-``None``
    ``os``/``arch`` fields) wins; ties are broken by most-recently
    registered.

    Args:
        initial_state: Optional initial mapping of package
            constraints. If provided, the state is copied to prevent
            external mutations.

    Example:
        ```pycon
        >>> from feu.compat import CompatRegistry, Target
        >>> from feu.compat.registry import VersionRange
        >>> registry = CompatRegistry()
        >>> registry.register(
        ...     pkg_name="numpy",
        ...     target=Target(python_version="3.11"),
        ...     ranges=[VersionRange("1.23.2", "2.4.6")],
        ... )
        >>> registry.is_valid_version("numpy", "2.0.2", Target(python_version="3.11"))
        True

        ```
    """

    def __init__(
        self, initial_state: dict[str, dict[Target, list[VersionRange]]] | None = None
    ) -> None:
        self._state: dict[str, dict[Target, list[VersionRange]]] = copy.deepcopy(
            initial_state or {}
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  {self._state}\n)"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def state(self) -> dict[str, dict[Target, list[VersionRange]]]:
        r"""The registered package constraints."""
        return self._state

    def register(
        self,
        pkg_name: str,
        target: Target,
        *,
        ranges: list[VersionRange],
        exist_ok: bool = False,
    ) -> None:
        r"""Register a package configuration for a compatibility target.

        Args:
            pkg_name: The package name to register (e.g., ``"numpy"``).
            target: The compatibility target.
            ranges: The list of valid version ranges for this target.
                An empty list means no version is valid.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when a
                configuration already exists for this package and
                target. Set to ``True`` to overwrite.

        Raises:
            RuntimeError: If a configuration already exists for the
                given package name and target, and ``exist_ok`` is
                ``False``.
        """
        table = self._state
        table[pkg_name] = table.get(pkg_name, {})

        if target in table[pkg_name] and not exist_ok:
            msg = (
                f"A package configuration ({table[pkg_name][target]}) is already "
                f"registered for package {pkg_name} and target {target}. Please "
                f"use `exist_ok=True` if you want to overwrite the package config"
            )
            raise RuntimeError(msg)

        table[pkg_name][target] = list(ranges)

    def register_many(
        self,
        mapping: dict[str, dict[Target, list[VersionRange]]],
        exist_ok: bool = False,
    ) -> None:
        r"""Register multiple package configurations at once.

        Args:
            mapping: Mapping of package name to ``Target`` to list of
                ``VersionRange``.
            exist_ok: Forwarded to ``register``.
        """
        for pkg_name, targets in mapping.items():
            for target, ranges in targets.items():
                self.register(
                    pkg_name=pkg_name,
                    target=target,
                    ranges=ranges,
                    exist_ok=exist_ok,
                )

    @staticmethod
    def _matches(entry_target: Target, lookup: Target) -> bool:
        if entry_target.python_version != lookup.python_version:
            return False
        if entry_target.free_threaded != lookup.free_threaded:
            return False
        if entry_target.os is not None and entry_target.os != lookup.os:
            return False
        return not (entry_target.arch is not None and entry_target.arch != lookup.arch)

    @staticmethod
    def _specificity(entry_target: Target) -> int:
        return (entry_target.os is not None) + (entry_target.arch is not None)

    def _resolve_ranges(self, pkg_name: str, target: Target) -> list[VersionRange] | None:
        r"""Resolve the raw registered ranges for a package/target,
        preserving the distinction between "no entry registered"
        (``None``) and "an entry registered with zero ranges" (``[]``,
        i.e. explicitly unsupported)."""
        if pkg_name not in self._state:
            return None
        best: list[VersionRange] | None = None
        best_specificity = -1
        for entry_target, ranges in self._state[pkg_name].items():
            if not self._matches(entry_target, target):
                continue
            specificity = self._specificity(entry_target)
            if specificity >= best_specificity:
                best_specificity = specificity
                best = ranges
        return best

    def get_config(self, pkg_name: str, target: Target) -> list[VersionRange]:
        r"""Get the list of valid version ranges for a package and
        compatibility target.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            The list of ``VersionRange`` for this target, or an empty
            list if no configuration matches.
        """
        return self._resolve_ranges(pkg_name, target) or []

    def is_unsupported(self, pkg_name: str, target: Target) -> bool:
        r"""Indicate if no package version is valid for a target.

        This is distinct from a target having no registered
        configuration at all: an unconfigured target is treated as
        permissive (``False``), whereas a target explicitly
        registered with an empty range list is unsupported
        (``True``).

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            ``True`` if the package has no valid version for the
            given target, ``False`` otherwise.
        """
        ranges = self._resolve_ranges(pkg_name, target)
        return ranges is not None and not ranges

    def get_version_ranges(
        self, pkg_name: str, target: Target
    ) -> list[tuple[Version | None, Version | None]]:
        r"""Get the valid version ranges as ``Version`` objects.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            A list of ``(min_version, max_version)`` tuples, either
            value being ``None`` if unconstrained on that side.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target.
        """
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            msg = f"No version of package {pkg_name} is compatible with target {target}"
            raise UnsupportedVersionError(msg)
        ranges = self.get_config(pkg_name=pkg_name, target=target)
        resolved = [
            (
                Version(version_range.min) if version_range.min is not None else None,
                Version(version_range.max) if version_range.max is not None else None,
            )
            for version_range in ranges
        ]
        # ``find_closest_version`` assumes ranges are sorted ascending by
        # min version, but registration order is not guaranteed to be sorted.
        resolved.sort(key=lambda r: (r[0] is not None, r[0]))
        return resolved

    def find_closest_version(self, pkg_name: str, pkg_version: str, target: Target) -> str:
        r"""Find the closest valid version for a package.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The requested package version.
            target: The compatibility target.

        Returns:
            The closest valid version as a string.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target.
        """
        version = Version(pkg_version)
        ranges = self.get_version_ranges(pkg_name=pkg_name, target=target)

        # If unconfigured (no ranges), return the input version
        if not ranges:
            return pkg_version

        for min_version, max_version in ranges:
            if (min_version is None or min_version <= version) and (
                max_version is None or version <= max_version
            ):
                return pkg_version

        if ranges[0][0] is not None and version < ranges[0][0]:
            return ranges[0][0].base_version
        if ranges[-1][1] is not None and version > ranges[-1][1]:
            return ranges[-1][1].base_version

        # In a gap between two ranges: snap up to the next range's min.
        for min_version, _ in ranges:
            if min_version is not None and version < min_version:
                return min_version.base_version

        # Unreachable: `version` is outside every range and not below the
        # first min or above the last max, so it must fall in a gap caught
        # above. Kept as a defensive guard for the exhaustiveness checker.
        msg = "unreachable: version did not match any range, boundary, or gap"  # pragma: no cover
        raise AssertionError(msg)  # pragma: no cover

    def is_valid_version(self, pkg_name: str, pkg_version: str, target: Target) -> bool:
        r"""Check if a package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The package version to validate.
            target: The compatibility target.

        Returns:
            ``True`` if valid for any registered range or
            unconfigured, ``False`` otherwise, including when no
            package version is valid for the given target.
        """
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            return False
        version = Version(pkg_version)
        ranges = self.get_version_ranges(pkg_name=pkg_name, target=target)
        # If unconfigured (no ranges), any version is valid
        if not ranges:
            return True
        return any(
            (min_version is None or min_version <= version)
            and (max_version is None or version <= max_version)
            for min_version, max_version in ranges
        )
