r"""Define the compatibility registry for package version resolution.

This module provides a registry system that manages and resolves valid
package version ranges per Python version, enabling lookup of the
closest valid version and validation of a given version.
"""

from __future__ import annotations

__all__ = ["CompatRegistry"]

import copy

from packaging.version import Version


class CompatRegistry:
    r"""Manage package version compatibility across different Python
    versions.

    This registry maintains package version constraints indexed by
    package name and Python version. Each entry specifies the minimum
    and maximum compatible versions for a package on a specific Python
    version.

    The registry state is structured as a nested dictionary::

        {
            package_name: {
                python_version: {
                    "min": minimum_version_string or None,
                    "max": maximum_version_string or None,
                },
                ...
            },
            ...
        }

    Args:
        initial_state: Optional initial mapping of package constraints.
            If provided, the state is copied to prevent external
            mutations.

    Example:
        ```pycon
        >>> from feu.compat import CompatRegistry
        >>> registry = CompatRegistry()
        >>> registry.register(
        ...     pkg_name="numpy",
        ...     python_version="3.11",
        ...     pkg_version_min="1.23.2",
        ...     pkg_version_max="2.4.6",
        ... )
        >>> registry.is_valid_version("numpy", "2.0.2", "3.11")
        True

        ```
    """

    def __init__(
        self, initial_state: dict[str, dict[str, dict[str, str | None]]] | None = None
    ) -> None:
        self.registry: dict[str, dict[str, dict[str, str | None]]] = copy.deepcopy(
            initial_state or {}
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  (registry): {self.registry}\n)"

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  (registry): {self.registry}\n)"

    def register(
        self,
        pkg_name: str,
        python_version: str,
        pkg_version_min: str | None,
        pkg_version_max: str | None,
        exist_ok: bool = False,
    ) -> None:
        r"""Register a package configuration for a Python version.

        Args:
            pkg_name: The package name to register (e.g., ``"numpy"``).
            python_version: The Python version (e.g., ``"3.11"``).
            pkg_version_min: The minimum valid package version for this
                Python version, or ``None`` for no minimum.
            pkg_version_max: The maximum valid package version for this
                Python version, or ``None`` for no maximum.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when a
                configuration already exists for this package and
                Python version. Set to ``True`` to overwrite.

        Raises:
            RuntimeError: If a configuration already exists for the
                given package name and Python version, and
                ``exist_ok`` is ``False``.
        """
        self.registry[pkg_name] = self.registry.get(pkg_name, {})

        if python_version in self.registry[pkg_name] and not exist_ok:
            msg = (
                f"A package configuration ({self.registry[pkg_name][python_version]}) is "
                f"already registered for package {pkg_name} and python {python_version}. "
                f"Please use `exist_ok=True` if you want to overwrite the package config"
            )
            raise RuntimeError(msg)

        self.registry[pkg_name][python_version] = {
            "min": pkg_version_min,
            "max": pkg_version_max,
        }

    def register_many(
        self,
        mapping: dict[str, dict[str, dict[str, str | None]]],
        exist_ok: bool = False,
    ) -> None:
        r"""Register multiple package configurations at once.

        Args:
            mapping: Mapping of package name to Python version to
                ``{"min": ..., "max": ...}`` constraints.
            exist_ok: If ``False``, a ``RuntimeError`` is raised when
                any entry already exists. Set to ``True`` to overwrite.
        """
        for pkg_name, versions in mapping.items():
            for python_version, config in versions.items():
                self.register(
                    pkg_name=pkg_name,
                    python_version=python_version,
                    pkg_version_min=config.get("min"),
                    pkg_version_max=config.get("max"),
                    exist_ok=exist_ok,
                )

    def get_config(self, pkg_name: str, python_version: str) -> dict[str, str | None]:
        r"""Get the package version configuration for a package and
        Python version.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            A dictionary with ``"min"`` and ``"max"`` keys, or an empty
            dictionary if no configuration exists.
        """
        if pkg_name not in self.registry:
            return {}
        return self.registry[pkg_name].get(python_version, {})

    def get_min_and_max_versions(
        self, pkg_name: str, python_version: str
    ) -> tuple[Version | None, Version | None]:
        r"""Get the minimum and maximum versions as ``Version`` objects.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            A tuple ``(min_version, max_version)``, either value being
            ``None`` if unconstrained or unconfigured.
        """
        config = self.get_config(pkg_name=pkg_name, python_version=python_version)
        min_version = config.get("min", None)
        max_version = config.get("max", None)
        if min_version is not None:
            min_version = Version(min_version)
        if max_version is not None:
            max_version = Version(max_version)
        return min_version, max_version

    def find_closest_version(self, pkg_name: str, pkg_version: str, python_version: str) -> str:
        r"""Find the closest valid version for a package.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The requested package version.
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            The closest valid version as a string.
        """
        version = Version(pkg_version)
        min_version, max_version = self.get_min_and_max_versions(
            pkg_name=pkg_name, python_version=python_version
        )
        if min_version is not None and version < min_version:
            return min_version.base_version
        if max_version is not None and version > max_version:
            return max_version.base_version
        return pkg_version

    def is_valid_version(self, pkg_name: str, pkg_version: str, python_version: str) -> bool:
        r"""Check if a package version is valid for a Python version.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The package version to validate.
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            ``True`` if valid or unconfigured, ``False`` otherwise.
        """
        version = Version(pkg_version)
        min_version, max_version = self.get_min_and_max_versions(
            pkg_name=pkg_name, python_version=python_version
        )
        return (min_version is None or min_version <= version) and (
            max_version is None or version <= max_version
        )
