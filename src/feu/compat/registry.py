r"""Define the compatibility registry for package version resolution.

This module provides a registry system that manages and resolves valid
package version ranges per compatibility target, enabling lookup of the
closest valid version and validation of a given version.
"""

from __future__ import annotations

__all__ = [
    "CompatRegistry",
    "DataLoader",
    "PackageData",
    "UnsupportedVersionError",
    "VersionRange",
]

import copy
from types import MappingProxyType
from typing import TYPE_CHECKING, NamedTuple, Protocol

from packaging.utils import canonicalize_name
from packaging.version import Version

from feu.version.request import parse_version_request

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Iterable, Mapping

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


class PackageData(NamedTuple):
    r"""Represent the compatibility data of one package.

    Args:
        targets: The ranges of each target.
    """

    targets: dict[Target, list[VersionRange]]


class DataLoader(Protocol):
    r"""Define the interface of the loader of the data of a registry.

    A registry asks its loader for the list of packages (cheap) and
    loads the data of a package the first time it needs it.
    """

    def packages(self) -> Collection[str]:
        r"""Get the canonical names of the packages that have data."""
        ...

    def load(self, name: str) -> PackageData:
        r"""Load the data of a package.

        Args:
            name: The canonical package name.
        """
        ...


def _parse(version: str | None) -> Version | None:
    r"""Parse an optional version string.

    Args:
        version: The version string, or ``None``.

    Returns:
        The parsed version, or ``None`` if ``version`` is ``None``.
    """
    return None if version is None else Version(version)


class UnsupportedVersionError(Exception):
    r"""Raised when no package version is compatible with a given
    target."""


class CompatRegistry:
    r"""Manage package version compatibility across different
    compatibility targets.

    The registry maps the canonical package name (PEP 503) to ``Target``
    to a list of
    ``VersionRange``. A package version is valid for a target if it
    falls within any of the registered ranges; an empty list means no
    version is valid for that target. A lookup target matches a
    stored entry when ``python_version`` and ``free_threaded`` are
    equal, and each of ``os``/``arch`` is ``None`` in the stored entry
    (wildcard), ``None`` in the lookup target (unspecified, i.e. any
    platform) or equal. Among all matching entries, the most specific
    ones (most non-``None`` ``os``/``arch`` fields) are kept and the
    answer is the union of their ranges. A lookup target that leaves
    ``os``/``arch`` to ``None`` therefore gets the versions published
    for at least one platform.

    Args:
        initial_state: Optional initial mapping of package
            constraints. If provided, the state is deep-copied to
            prevent external mutations. It is validated like
            ``register``, and the package names are canonicalised.
        loader: Optional loader of the data of the packages. The data
            of a package is loaded the first time the package is
            looked up or registered into, so creating the registry
            and listing its packages cost nothing. A registration into
            a package that is not loaded yet loads it first, so the
            conflict check and ``exist_ok`` see the loaded entries.
        version_source: Optional function that returns the releases of
            a package (given its canonical name), in any order. It is
            called only to match a wildcard request (e.g. ``"2.*"``)
            or to list versions, never for an exact version or for
            the latest version, and only for a package that has
            ranges. The versions registered with ``register_versions``
            take precedence. Without a source, a wildcard can only be
            matched against registered versions. An error of the
            source (e.g. no network) is not caught.

    Raises:
        ValueError: If a range of ``initial_state`` is invalid (see
            ``register``).

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
        self,
        initial_state: dict[str, dict[Target, list[VersionRange]]] | None = None,
        *,
        loader: DataLoader | None = None,
        version_source: Callable[[str], Iterable[str]] | None = None,
    ) -> None:
        self._state: dict[str, dict[Target, list[VersionRange]]] = {}
        self._versions: dict[str, tuple[str, ...]] = {}
        self._loader = loader
        self._version_source = version_source
        self._loaded: set[str] = set()
        self.register_many(copy.deepcopy(initial_state or {}))

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(packages={len(self.packages())})"

    def __str__(self) -> str:
        return self.__repr__()

    def _ensure_loaded(self, name: str) -> None:
        r"""Load the data of a package from the loader, once.

        Args:
            name: The canonical package name.
        """
        if self._loader is None or name in self._loaded:
            return
        self._loaded.add(name)
        if name not in self._loader.packages():
            return
        data = self._loader.load(name)
        for target, ranges in data.targets.items():
            self._validate_ranges(name, ranges)
            self._state.setdefault(name, {})[target] = list(ranges)

    def _has_data(self, name: str) -> bool:
        r"""Indicate if the registry has data for a package.

        Args:
            name: The canonical package name. Its data must be loaded.

        Returns:
            ``True`` if the package has ranges or registered versions.
        """
        return name in self._state or name in self._versions

    def _can_list_versions(self, name: str) -> bool:
        r"""Indicate if the versions of a package can be listed.

        Args:
            name: The canonical package name. Its data must be loaded.

        Returns:
            ``True`` if versions are registered for the package, or if
                the package has ranges and a version source is set.
        """
        return name in self._versions or (self._version_source is not None and name in self._state)

    def _known_versions(self, name: str) -> tuple[str, ...]:
        r"""Get the known versions of a package.

        Args:
            name: The canonical package name. Its data must be loaded.

        Returns:
            The registered versions if there are some, else the
                versions of the source (if the package has ranges),
                else an empty tuple. In PEP 440 order.
        """
        if name in self._versions:
            return self._versions[name]
        if self._version_source is not None and name in self._state:
            return tuple(sorted(dict.fromkeys(self._version_source(name)), key=Version))
        return ()

    @property
    def state(self) -> Mapping[str, Mapping[Target, list[VersionRange]]]:
        r"""A read-only view of the registered package constraints, as a
        mapping of canonical package name to ``Target`` to a list of
        ``VersionRange``.

        Reading it loads the data of every package of the loader.
        """
        for name in self.packages():
            self._ensure_loaded(name)
        return MappingProxyType({name: MappingProxyType(c) for name, c in self._state.items()})

    def packages(self) -> list[str]:
        r"""Get the packages of the registry.

        Returns:
            The sorted canonical names of the registered packages and
                of the packages that the loader can load. No data is
                loaded.

        Example:
            ```pycon
            >>> from feu.compat import CompatRegistry, Target, VersionRange
            >>> registry = CompatRegistry({"NumPy": {Target("3.11"): [VersionRange("1.0", None)]}})
            >>> registry.packages()
            ['numpy']

            ```
        """
        names = set(self._state)
        if self._loader is not None:
            names.update(self._loader.packages())
        return sorted(names)

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
                It is canonicalised (PEP 503).
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
            ValueError: If a bound of a range is not a valid PEP 440
                version, or if a minimum is greater than the maximum
                of the same range. Nothing is registered in that case.
        """
        name = canonicalize_name(pkg_name)
        self._validate_ranges(name, ranges)
        self._ensure_loaded(name)
        configs = self._state.get(name, {})

        if target in configs and not exist_ok:
            msg = (
                f"A package configuration ({configs[target]}) is already "
                f"registered for package {name} and target {target}. Please "
                f"use `exist_ok=True` if you want to overwrite the package config"
            )
            raise RuntimeError(msg)

        self._state.setdefault(name, {})[target] = list(ranges)

    @staticmethod
    def _validate_ranges(pkg_name: str, ranges: list[VersionRange]) -> None:
        r"""Validate a list of version ranges.

        Args:
            pkg_name: The package name, used in the error message.
            ranges: The ranges to validate.

        Raises:
            ValueError: If a bound is not a valid PEP 440 version, or
                if a minimum is greater than the maximum of the same
                range.
        """
        for version_range in ranges:
            min_version = _parse(version_range.min)
            max_version = _parse(version_range.max)
            if min_version is not None and max_version is not None and min_version > max_version:
                msg = (
                    f"invalid version range {tuple(version_range)} for package {pkg_name}: "
                    "the minimum is greater than the maximum"
                )
                raise ValueError(msg)

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

        Raises:
            RuntimeError: If any configuration already exists for a
                given package name and target, and ``exist_ok`` is
                ``False``.
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
        r"""Indicate if a registered target applies to a lookup target.

        Args:
            entry_target: The registered target. Its ``os`` and
                ``arch`` act as wildcards when they are ``None``.
            lookup: The target to look up. Its ``os`` and ``arch``
                act as wildcards when they are ``None`` ("any
                platform").

        Returns:
            ``True`` if ``python_version`` and ``free_threaded`` are
                equal, and each of ``os`` and ``arch`` is ``None`` in
                ``entry_target``, ``None`` in ``lookup`` or equal.
        """
        if entry_target.python_version != lookup.python_version:
            return False
        if entry_target.free_threaded != lookup.free_threaded:
            return False
        if entry_target.os is not None and lookup.os is not None and entry_target.os != lookup.os:
            return False
        return not (
            entry_target.arch is not None
            and lookup.arch is not None
            and entry_target.arch != lookup.arch
        )

    @staticmethod
    def _specificity(entry_target: Target) -> int:
        r"""Compute how specific a registered target is.

        Args:
            entry_target: The registered target.

        Returns:
            The number of non-``None`` fields among ``os`` and
                ``arch``, i.e. ``0``, ``1`` or ``2``.
        """
        return (entry_target.os is not None) + (entry_target.arch is not None)

    @staticmethod
    def _merge_ranges(ranges: list[VersionRange]) -> list[VersionRange]:
        r"""Merge overlapping version ranges.

        Args:
            ranges: The ranges to merge. They can be in any order.

        Returns:
            The union of the ranges, sorted by ascending minimum
                version. Two ranges that overlap (the bounds are
                inclusive) are merged into one.
        """
        parsed = sorted(
            ((_parse(r.min), _parse(r.max), r) for r in ranges),
            key=lambda item: (item[0] is not None, item[0] or Version("0")),
        )
        merged: list[VersionRange] = []
        merged_max: Version | None = None
        for min_version, max_version, version_range in parsed:
            if merged and (merged_max is None or min_version is None or min_version <= merged_max):
                if merged_max is not None and (max_version is None or max_version > merged_max):
                    merged[-1] = VersionRange(merged[-1].min, version_range.max)
                    merged_max = max_version
                continue
            merged.append(version_range)
            merged_max = max_version
        return merged

    def _resolve_ranges(self, pkg_name: str, target: Target) -> list[VersionRange] | None:
        r"""Resolve the raw registered ranges for a package/target,
        preserving the distinction between "no entry registered"
        (``None``) and "an entry registered with zero ranges" (``[]``,
        i.e. explicitly unsupported).

        Args:
            pkg_name: The package name to query.
            target: The compatibility target.

        Returns:
            The union of the ranges of the most specific entries
                matching ``target``, or ``None`` if no entry
                matches.
        """
        name = canonicalize_name(pkg_name)
        self._ensure_loaded(name)
        configs = self._state.get(name)
        if configs is None:
            return None
        best: list[list[VersionRange]] = []
        best_specificity = -1
        for entry_target, ranges in configs.items():
            if not self._matches(entry_target, target):
                continue
            specificity = self._specificity(entry_target)
            if specificity > best_specificity:
                best_specificity = specificity
                best = []
            if specificity == best_specificity:
                best.append(ranges)
        if not best:
            return None
        if len(best) == 1:
            return best[0]
        return self._merge_ranges([r for ranges in best for r in ranges])

    def has_package(self, pkg_name: str) -> bool:
        r"""Indicate if at least one configuration is registered for a
        package.

        An unknown package is permissive (any version is valid), so
        this method lets the caller detect that case.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).

        Returns:
            ``True`` if a configuration is registered for the
                package, otherwise ``False``.
        """
        name = canonicalize_name(pkg_name)
        self._ensure_loaded(name)
        return bool(self._state.get(name))

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
            A list of ``(min_version, max_version)`` tuples sorted by
                ascending minimum version, either value being ``None``
                if unconstrained on that side. The list is empty if
                the package is not configured for the target.

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

    def _find_closest_exact_version(self, pkg_name: str, pkg_version: str, target: Target) -> str:
        r"""Find the closest valid version for an exact version.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The requested exact package version.
            target: The compatibility target.

        Returns:
            The requested version if it is valid or if the package is
                not configured for the target, otherwise the nearest
                range boundary, as it was registered.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target.
        """
        version = Version(pkg_version)
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            msg = f"No version of package {pkg_name} is compatible with target {target}"
            raise UnsupportedVersionError(msg)
        # ``VersionRange`` keeps the registered strings, which are returned
        # as is for a boundary. The ranges are sorted ascending by min
        # version, but registration order is not guaranteed to be sorted.
        ranges = sorted(
            self.get_config(pkg_name=pkg_name, target=target),
            key=lambda r: (r.min is not None, _parse(r.min)),
        )

        # If unconfigured (no ranges), return the input version
        if not ranges:
            return pkg_version

        for version_range in ranges:
            min_version = _parse(version_range.min)
            max_version = _parse(version_range.max)
            if (min_version is None or min_version <= version) and (
                max_version is None or version <= max_version
            ):
                return pkg_version

        if ranges[0].min is not None and version < Version(ranges[0].min):
            return ranges[0].min
        if ranges[-1].max is not None and version > Version(ranges[-1].max):
            return ranges[-1].max

        # In a gap between two ranges: snap up to the next range's min.
        for version_range in ranges:
            if version_range.min is not None and version < Version(version_range.min):
                return version_range.min

        # Unreachable: `version` is outside every range and not below the
        # first min or above the last max, so it must fall in a gap caught
        # above. Kept as a defensive guard for the exhaustiveness checker.
        msg = "unreachable: version did not match any range, boundary, or gap"  # pragma: no cover
        raise AssertionError(msg)  # pragma: no cover

    def _is_valid_exact_version(self, pkg_name: str, pkg_version: str, target: Target) -> bool:
        r"""Check if an exact package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The exact package version to validate.
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
        return not ranges or self._in_ranges(version, ranges)

    def register_versions(
        self, pkg_name: str, versions: Iterable[str], *, exist_ok: bool = False
    ) -> None:
        r"""Register the versions the registry knows for a package.

        A wildcard or empty version request (e.g. ``"2.*"``) is matched
        against these versions.

        Args:
            pkg_name: The package name (e.g., ``"numpy"``). It is
                canonicalised (PEP 503).
            versions: The known versions, in any order. Duplicates are
                removed and the versions are sorted by PEP 440 order.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when
                versions are already registered for the package. Set
                to ``True`` to overwrite.

        Raises:
            RuntimeError: If versions are already registered for the
                package and ``exist_ok`` is ``False``.
            packaging.version.InvalidVersion: If a version is not a
                valid PEP 440 version.

        Example:
            ```pycon
            >>> from feu.compat import CompatRegistry
            >>> registry = CompatRegistry()
            >>> registry.register_versions("numpy", ["2.0.0", "1.26.4", "2.0.2"])

            ```
        """
        name = canonicalize_name(pkg_name)
        self._ensure_loaded(name)
        if name in self._versions and not exist_ok:
            msg = (
                f"Versions are already registered for package {name}. Please use "
                "`exist_ok=True` if you want to overwrite them"
            )
            raise RuntimeError(msg)
        self._versions[name] = tuple(sorted(dict.fromkeys(versions), key=Version))

    def get_compatible_versions(
        self, pkg_name: str, target: Target, pkg_version: str | None = ""
    ) -> list[str]:
        r"""Get the known versions that are valid for a target and
        satisfy a version request.

        Args:
            pkg_name: The package name (e.g., ``"numpy"``).
            target: The compatibility target.
            pkg_version: The version request: an exact version, a
                wildcard (e.g. ``"2.*"``) or ``""``/``None`` for every
                version.

        Returns:
            The known versions that lie in a valid range of the
                target and satisfy the request, in PEP 440 order. The
                versions are the registered ones or, if there are none,
                the ones of the version source (downloaded when the
                method is called). The list is empty if the package
                has no data, if no version is valid for the target, or
                if nothing matches. A package
                that has no configuration for the target accepts every
                known version.

        Raises:
            ValueError: If ``pkg_version`` is not a valid version
                request.

        Example:
            ```pycon
            >>> from feu.compat import CompatRegistry, Target, VersionRange
            >>> target = Target(python_version="3.11")
            >>> registry = CompatRegistry({"numpy": {target: [VersionRange("1.0.0", "1.26.4")]}})
            >>> registry.register_versions("numpy", ["1.0.0", "1.26.4", "2.0.0"])
            >>> registry.get_compatible_versions("numpy", target)
            ['1.0.0', '1.26.4']
            >>> registry.get_compatible_versions("numpy", target, "2.*")
            []

            ```
        """
        request = parse_version_request(pkg_version)
        name = canonicalize_name(pkg_name)
        self._ensure_loaded(name)
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            return []
        ranges = self.get_version_ranges(pkg_name=pkg_name, target=target)
        return [
            version
            for version in self._known_versions(name)
            if request.matches(Version(version))
            and (not ranges or self._in_ranges(Version(version), ranges))
        ]

    @staticmethod
    def _in_ranges(version: Version, ranges: list[tuple[Version | None, Version | None]]) -> bool:
        r"""Indicate if a version lies in at least one range.

        Args:
            version: The version to check.
            ranges: The ``(min, max)`` ranges, a ``None`` bound being
                unconstrained.

        Returns:
            ``True`` if ``version`` is in a range, otherwise
                ``False``.
        """
        return any(
            (min_version is None or min_version <= version)
            and (max_version is None or version <= max_version)
            for min_version, max_version in ranges
        )

    def _find_closest_latest(self, pkg_name: str, target: Target) -> str:
        r"""Find the version to install for the latest version.

        No version is downloaded: the latest compatible version is
        either unbounded (a range is open) or the highest upper bound.

        Args:
            pkg_name: The package name (e.g., ``"numpy"``). Its data
                must be loaded and it must have data.
            target: The compatibility target.

        Returns:
            ``""`` if the package is not configured for the target or
                if a range is open, otherwise the highest upper bound,
                as it was registered.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target.
        """
        ranges = self.get_version_ranges(pkg_name=pkg_name, target=target)
        if not ranges or any(max_version is None for _, max_version in ranges):
            return ""
        bounds = [r.max for r in self.get_config(pkg_name=pkg_name, target=target)]
        return max((b for b in bounds if b is not None), key=Version)

    def find_closest_version(self, pkg_name: str, pkg_version: str | None, target: Target) -> str:
        r"""Find the closest valid version for a package.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The requested package version: an exact
                version (e.g. ``"2.0.2"``), a wildcard (e.g.
                ``"2.*"``) or ``""``/``None`` for the latest
                version.
            target: The compatibility target.

        Returns:
            The version to install, as a string.

            - For an exact version: the version itself if it is valid
              or if the package is not configured for the target,
              otherwise the nearest range boundary, as it was
              registered.
            - For the latest version (``""``/``None``): the request
              itself if a range is open-ended, otherwise the highest
              upper bound. No version is downloaded.
            - For a wildcard: the latest known compatible version
              that satisfies the request (the versions are the
              registered ones or the ones of the version source, so
              they are up to date). If it lies in an open-ended
              range, the request itself is returned (``"2.*"``) so
              that the installer picks the real latest release.
            - If the registry has no data for the package, the
              request is returned unchanged.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target, or if no known version
                satisfies a wildcard request.
            ValueError: If ``pkg_version`` is not a valid version
                request.

        Example:
            ```pycon
            >>> from feu.compat import CompatRegistry, Target, VersionRange
            >>> target = Target(python_version="3.11")
            >>> registry = CompatRegistry({"numpy": {target: [VersionRange("1.0.0", "1.26.4")]}})
            >>> registry.register_versions("numpy", ["1.0.0", "1.26.4", "2.0.0"])
            >>> registry.find_closest_version("numpy", "2.0.0", target)
            '1.26.4'
            >>> registry.find_closest_version("numpy", "", target)
            '1.26.4'

            ```
        """
        request = parse_version_request(pkg_version)
        if request.exact is not None:
            return self._find_closest_exact_version(pkg_name, request.text, target)
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            msg = f"No version of package {pkg_name} is compatible with target {target}"
            raise UnsupportedVersionError(msg)
        name = canonicalize_name(pkg_name)
        self._ensure_loaded(name)
        if not self._has_data(name):
            return request.text
        if request.is_latest:
            return self._find_closest_latest(pkg_name, target)
        if not self._can_list_versions(name):
            return request.text
        ranges = self.get_version_ranges(pkg_name=pkg_name, target=target)
        compatible = self.get_compatible_versions(pkg_name, target, request.text)
        if not compatible:
            msg = f"No version of package {pkg_name} matches {request.text!r} for target {target}"
            raise UnsupportedVersionError(msg)
        latest = Version(compatible[-1])
        if not ranges or any(
            max_version is None and (min_version is None or min_version <= latest)
            for min_version, max_version in ranges
        ):
            return request.text
        return compatible[-1]

    def is_valid_version(self, pkg_name: str, pkg_version: str | None, target: Target) -> bool:
        r"""Check if a package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The package version request: an exact
                version, a wildcard (e.g. ``"2.*"``) or
                ``""``/``None`` for the latest version.
            target: The compatibility target.

        Returns:
            For an exact version: ``True`` if valid for any registered
            range or unconfigured, ``False`` otherwise, including when
            no package version is valid for the given target. For a
            wildcard: ``True`` if at least one known compatible
            version satisfies the request (see
            ``get_compatible_versions``, which downloads the
            versions); a package without data gives ``False``. For
            the latest version: ``True`` if the registry has data for
            the package and a version is valid for the target; no
            version is downloaded.

        Raises:
            ValueError: If ``pkg_version`` is not a valid version
                request.

        Example:
            ```pycon
            >>> from feu.compat import CompatRegistry, Target, VersionRange
            >>> target = Target(python_version="3.11")
            >>> registry = CompatRegistry({"numpy": {target: [VersionRange("1.0.0", "1.26.4")]}})
            >>> registry.register_versions("numpy", ["1.0.0", "1.26.4", "2.0.0"])
            >>> registry.is_valid_version("numpy", "1.*", target)
            True
            >>> registry.is_valid_version("numpy", "2.*", target)
            False

            ```
        """
        request = parse_version_request(pkg_version)
        if request.exact is not None:
            return self._is_valid_exact_version(pkg_name, request.text, target)
        if request.is_latest:
            name = canonicalize_name(pkg_name)
            self._ensure_loaded(name)
            return self._has_data(name) and not self.is_unsupported(
                pkg_name=pkg_name, target=target
            )
        return bool(self.get_compatible_versions(pkg_name, target, request.text))
