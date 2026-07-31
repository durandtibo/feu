r"""Define the compatibility registry for package version resolution.

This module provides a registry system that manages and resolves valid
package version ranges per compatibility target, enabling lookup of
the closest valid version and validation of a given version.
"""

from __future__ import annotations

__all__ = ["UNSUPPORTED", "CompatRegistry", "UnsupportedVersionError"]

import copy
from typing import TYPE_CHECKING, Literal

from packaging.version import Version

if TYPE_CHECKING:
    from feu.compat.target import Target

UNSUPPORTED = "unsupported"
r"""Sentinel used as the ``min``/``max`` value to mark a target for
which no package version is valid.

This is distinct from ``None``, which means "unconstrained" (i.e. any
version is valid).
"""

_Layer = Literal["base", "override"]


class UnsupportedVersionError(Exception):
    r"""Raised when no package version is compatible with a given
    target."""


class CompatRegistry:
    r"""Manage package version compatibility across different
    compatibility targets.

    The registry holds two independent layers per package:

    - ``base``: populated by ``register_defaults`` and discovered
      data. Entries here can be freely refreshed (e.g. by re-running
      discovery) without ever conflicting with user overrides.
    - ``overrides``: populated by user calls (``register_compat`` /
      ``register(layer="override")``, the default). Overrides always
      take precedence over ``base`` and are only conflict-checked
      against other overrides.

    Each layer maps package name to ``Target`` to ``{"min": ...,
    "max": ...}``. A lookup target matches a stored entry when
    ``python_version`` and ``free_threaded`` are equal, and the
    stored entry's ``os``/``arch`` are either ``None`` (wildcard) or
    equal to the lookup target's ``os``/``arch``. Among all matching
    entries in a layer, the most specific one (most non-``None``
    ``os``/``arch`` fields) wins; ties are broken by most-recently
    registered.

    Args:
        initial_state: Optional initial mapping of package
            constraints, seeding the ``base`` layer. If provided, the
            state is copied to prevent external mutations.

    Example:
        ```pycon
        >>> from feu.compat import CompatRegistry, Target
        >>> registry = CompatRegistry()
        >>> registry.register(
        ...     pkg_name="numpy",
        ...     target=Target(python_version="3.11"),
        ...     pkg_version_min="1.23.2",
        ...     pkg_version_max="2.4.6",
        ...     layer="base",
        ... )
        >>> registry.is_valid_version("numpy", "2.0.2", Target(python_version="3.11"))
        True

        ```
    """

    def __init__(
        self, initial_state: dict[str, dict[Target, dict[str, str | None]]] | None = None
    ) -> None:
        self._base: dict[str, dict[Target, dict[str, str | None]]] = copy.deepcopy(
            initial_state or {}
        )
        self._overrides: dict[str, dict[Target, dict[str, str | None]]] = {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(\n"
            f"  (base): {self._base}\n"
            f"  (overrides): {self._overrides}\n)"
        )

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def base(self) -> dict[str, dict[Target, dict[str, str | None]]]:
        r"""The base layer (defaults/discovered data)."""
        return self._base

    @property
    def overrides(self) -> dict[str, dict[Target, dict[str, str | None]]]:
        r"""The override layer (user-supplied corrections)."""
        return self._overrides

    def _layer_table(self, layer: _Layer) -> dict[str, dict[Target, dict[str, str | None]]]:
        return self._base if layer == "base" else self._overrides

    def register(
        self,
        pkg_name: str,
        target: Target,
        *,
        pkg_version_min: str | None,
        pkg_version_max: str | None,
        exist_ok: bool = False,
        layer: _Layer = "override",
    ) -> None:
        r"""Register a package configuration for a compatibility
        target.

        Args:
            pkg_name: The package name to register (e.g., ``"numpy"``).
            target: The compatibility target.
            pkg_version_min: The minimum valid package version for
                this target, or ``None`` for no minimum.
            pkg_version_max: The maximum valid package version for
                this target, or ``None`` for no maximum.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when a
                configuration already exists for this package and
                target **within the same layer**. Set to ``True`` to
                overwrite.
            layer: Which layer to write to, ``"base"`` or
                ``"override"``. Defaults to ``"override"``, matching
                the public ``register_compat`` behavior.

        Raises:
            RuntimeError: If a configuration already exists for the
                given package name and target in the same layer, and
                ``exist_ok`` is ``False``.
        """
        table = self._layer_table(layer)
        table[pkg_name] = table.get(pkg_name, {})

        if target in table[pkg_name] and not exist_ok:
            msg = (
                f"A package configuration ({table[pkg_name][target]}) is already "
                f"registered for package {pkg_name} and target {target} in the "
                f"'{layer}' layer. Please use `exist_ok=True` if you want to "
                f"overwrite the package config"
            )
            raise RuntimeError(msg)

        table[pkg_name][target] = {"min": pkg_version_min, "max": pkg_version_max}

    def register_many(
        self,
        mapping: dict[str, dict[Target, dict[str, str | None]]],
        exist_ok: bool = False,
        layer: _Layer = "override",
    ) -> None:
        r"""Register multiple package configurations at once.

        Args:
            mapping: Mapping of package name to ``Target`` to
                ``{"min": ..., "max": ...}`` constraints.
            exist_ok: Forwarded to ``register``.
            layer: Forwarded to ``register``.
        """
        for pkg_name, targets in mapping.items():
            for target, config in targets.items():
                self.register(
                    pkg_name=pkg_name,
                    target=target,
                    pkg_version_min=config.get("min"),
                    pkg_version_max=config.get("max"),
                    exist_ok=exist_ok,
                    layer=layer,
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

    def _resolve_in_layer(
        self, table: dict[str, dict[Target, dict[str, str | None]]], pkg_name: str, target: Target
    ) -> dict[str, str | None] | None:
        if pkg_name not in table:
            return None
        best: dict[str, str | None] | None = None
        best_specificity = -1
        for entry_target, config in table[pkg_name].items():
            if not self._matches(entry_target, target):
                continue
            specificity = self._specificity(entry_target)
            if specificity >= best_specificity:
                best_specificity = specificity
                best = config
        return best

    def get_config(self, pkg_name: str, target: Target) -> dict[str, str | None]:
        r"""Get the package version configuration for a package and
        compatibility target.

        Checks the override layer first, then falls back to the base
        layer.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            A dictionary with ``"min"`` and ``"max"`` keys, or an
            empty dictionary if no configuration matches.
        """
        config = self._resolve_in_layer(self._overrides, pkg_name, target)
        if config is not None:
            return config
        return self._resolve_in_layer(self._base, pkg_name, target) or {}

    def is_unsupported(self, pkg_name: str, target: Target) -> bool:
        r"""Indicate if no package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            ``True`` if the package has no valid version for the
            given target, ``False`` otherwise.
        """
        config = self.get_config(pkg_name=pkg_name, target=target)
        return config.get("min") == UNSUPPORTED or config.get("max") == UNSUPPORTED

    def get_min_and_max_versions(
        self, pkg_name: str, target: Target
    ) -> tuple[Version | None, Version | None]:
        r"""Get the minimum and maximum versions as ``Version``
        objects.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            target: The compatibility target.

        Returns:
            A tuple ``(min_version, max_version)``, either value being
            ``None`` if unconstrained or unconfigured.

        Raises:
            UnsupportedVersionError: If no package version is valid
                for the given target.
        """
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            msg = f"No version of package {pkg_name} is compatible with target {target}"
            raise UnsupportedVersionError(msg)
        config = self.get_config(pkg_name=pkg_name, target=target)
        min_version = config.get("min", None)
        max_version = config.get("max", None)
        if min_version is not None:
            min_version = Version(min_version)
        if max_version is not None:
            max_version = Version(max_version)
        return min_version, max_version

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
        min_version, max_version = self.get_min_and_max_versions(pkg_name=pkg_name, target=target)
        if min_version is not None and version < min_version:
            return min_version.base_version
        if max_version is not None and version > max_version:
            return max_version.base_version
        return pkg_version

    def is_valid_version(self, pkg_name: str, pkg_version: str, target: Target) -> bool:
        r"""Check if a package version is valid for a target.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The package version to validate.
            target: The compatibility target.

        Returns:
            ``True`` if valid or unconfigured, ``False`` otherwise,
            including when no package version is valid for the given
            target.
        """
        if self.is_unsupported(pkg_name=pkg_name, target=target):
            return False
        version = Version(pkg_version)
        min_version, max_version = self.get_min_and_max_versions(pkg_name=pkg_name, target=target)
        return (min_version is None or min_version <= version) and (
            max_version is None or version <= max_version
        )
