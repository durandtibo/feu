r"""Provide package version compatibility checking functionality.

This module provides a registry-based system for managing package version
constraints across different Python versions. It allows you to:

- Define minimum and maximum package version constraints for each Python version
- Validate if a package version is compatible with a specific Python version
- Find the closest valid package version when a requested version is out of range
- Maintain a centralized registry of version constraints for common packages

The main class ``PackageConfig`` provides both class methods for direct use and
a registry that can be extended with custom package configurations.
"""

from __future__ import annotations

__all__ = ["PackageConfig", "find_closest_version", "is_valid_version"]

import logging
from typing import ClassVar

from packaging.version import Version

logger: logging.Logger = logging.getLogger(__name__)


class PackageConfig:
    r"""Manage package version compatibility across different Python
    versions.

    This class maintains a registry of package version constraints indexed by
    package name and Python version. Each entry specifies the minimum and
    maximum compatible versions for a package on a specific Python version.

    The registry is structured as a nested dictionary:
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

    Use cases:
        - Check if a package version is valid for a Python version
        - Find the closest valid version for a package
        - Add custom package configurations
        - Query version constraints for package/Python version combinations

    Example:
        ```pycon
        >>> from feu.package import PackageConfig
        >>> # Check if numpy 2.0.2 is valid for Python 3.11
        >>> PackageConfig.is_valid_version("numpy", "2.0.2", "3.11")
        True
        >>> # Get version constraints
        >>> PackageConfig.get_config("numpy", "3.11")
        {'min': '1.23.2', 'max': None}
        >>> # Find closest valid version
        >>> PackageConfig.find_closest_version("numpy", "1.0.0", "3.11")
        '1.23.2'

        ```

    Attributes:
        registry: Class-level registry storing package version constraints.
            The structure is a three-level nested dictionary mapping
            package names to Python versions to version constraints.
    """

    registry: ClassVar[dict[str, dict[str, dict[str, str | None]]]] = {
        # https://click.palletsprojects.com/en/stable/changes/
        "click": {
            "3.14": {"min": None, "max": None},
            "3.13": {"min": None, "max": None},
            "3.12": {"min": None, "max": None},
            "3.11": {"min": None, "max": None},
            "3.10": {"min": None, "max": None},
            "3.9": {"min": None, "max": "8.1.8"},
        },
        # https://pypi.org/project/jaxlib/#history
        "jax": {
            "3.14": {"min": "0.9.0", "max": None},
            "3.13": {"min": "0.9.0", "max": None},
            "3.12": {"min": "0.9.0", "max": None},
            "3.11": {"min": "0.9.0", "max": None},
            "3.10": {"min": "0.4.6", "max": "0.6.2"},
            "3.9": {"min": "0.4.6", "max": "0.4.30"},
        },
        # https://matplotlib.org/stable/users/release_notes.html
        "matplotlib": {
            "3.14": {"min": "3.10.5", "max": None},
            "3.13": {"min": "3.10.0", "max": None},
            "3.12": {"min": "3.10.0", "max": None},
            "3.11": {"min": "3.10.0", "max": None},
            "3.10": {"min": "3.10.0", "max": None},
            "3.9": {"min": None, "max": "3.9.4"},
        },
        # https://numpy.org/devdocs/release.html
        "numpy": {
            "3.14": {"min": "2.4.0", "max": None},
            "3.13": {"min": "2.1.0", "max": None},
            "3.12": {"min": "1.26.0", "max": None},
            "3.11": {"min": "2.0.0", "max": None},
            "3.10": {"min": "1.21.3", "max": "2.2.6"},
            "3.9": {"min": "1.19.3", "max": "2.0.2"},
        },
        # https://github.com/pandas-dev/pandas/releases
        # https://pandas.pydata.org/docs/whatsnew/index.html
        "pandas": {
            "3.14": {"min": "3.0.0", "max": None},
            "3.13": {"min": "3.0.0", "max": None},
            "3.12": {"min": "3.0.0", "max": None},
            "3.11": {"min": "3.0.0", "max": None},
            "3.10": {"min": "1.3.3", "max": "2.3.3"},
            "3.9": {"min": None, "max": "2.3.3"},
        },
        # https://arrow.apache.org/release/
        "pyarrow": {
            "3.14": {"min": "22.0.0", "max": None},
            "3.13": {"min": "18.0.0", "max": None},
            "3.12": {"min": "14.0.0", "max": None},
            "3.11": {"min": "10.0.1", "max": None},
            "3.10": {"min": "6.0.0", "max": None},
            "3.9": {"min": "3.0.0", "max": "18.0.0"},
        },
        "requests": {
            "3.14": {"min": None, "max": None},
            "3.13": {"min": None, "max": None},
            "3.12": {"min": None, "max": None},
            "3.11": {"min": None, "max": None},
            "3.10": {"min": None, "max": None},
            "3.9": {"min": None, "max": None},
        },
        # https://github.com/scikit-learn/scikit-learn/releases
        "scikit-learn": {
            "3.14": {"min": "1.8.0", "max": None},
            "3.13": {"min": "1.8.0", "max": None},
            "3.12": {"min": "1.8.0", "max": None},
            "3.11": {"min": "1.8.0", "max": None},
            "3.10": {"min": "1.1.0", "max": "1.7.2"},
            "3.9": {"min": None, "max": "1.6.1"},
        },
        # https://github.com/scipy/scipy/releases/
        "scipy": {
            "3.14": {"min": "1.17.0", "max": None},
            "3.13": {"min": "1.17.0", "max": None},
            "3.12": {"min": "1.17.0", "max": None},
            "3.11": {"min": "1.17.0", "max": None},
            "3.10": {"min": "1.8.0", "max": "1.15.3"},
            "3.9": {"min": None, "max": "1.13.1"},
        },
        # https://github.com/pytorch/pytorch/releases
        "torch": {
            "3.14": {"min": "2.10.0", "max": None},
            "3.13": {"min": "2.10.0", "max": None},
            "3.12": {"min": "2.10.0", "max": None},
            "3.11": {"min": "2.10.0", "max": None},
            "3.10": {"min": "1.11.0", "max": None},
            "3.9": {"min": None, "max": "2.8.0"},
        },
        # https://docs.xarray.dev/en/stable/whats-new.html
        "xarray": {
            "3.14": {"min": "2025.12.0", "max": None},
            "3.13": {"min": "2025.12.0", "max": None},
            "3.12": {"min": "2025.12.0", "max": None},
            "3.11": {"min": "2025.12.0", "max": None},
            "3.10": {"min": None, "max": "2025.6.1"},
            "3.9": {"min": None, "max": "2024.7.0"},
        },
    }

    @classmethod
    def add_config(
        cls,
        pkg_name: str,
        pkg_version_min: str | None,
        pkg_version_max: str | None,
        python_version: str,
        exist_ok: bool = False,
    ) -> None:
        r"""Add a new package configuration to the registry.

        This method registers version constraints for a package on a specific
        Python version. If a configuration already exists for the package and
        Python version, ``exist_ok`` must be ``True`` to allow overwriting.

        Args:
            pkg_name: The package name to register (e.g., ``"numpy"``).
            pkg_version_min: The minimum valid package version for this
                Python version. Use ``None`` if there is no minimum version
                constraint.
            pkg_version_max: The maximum valid package version for this
                Python version. Use ``None`` if there is no maximum version
                constraint.
            python_version: The Python version (e.g., ``"3.11"``).
            exist_ok: If ``False``, a ``RuntimeError`` is raised when a
                package configuration already exists for this package and
                Python version. Set to ``True`` to overwrite the existing
                configuration. Defaults to ``False``.

        Raises:
            RuntimeError: If a package configuration already exists for the
                given package name and Python version, and ``exist_ok`` is
                ``False``.

        Example:
            ```pycon
            >>> from feu.package import PackageConfig
            >>> # Add a new package configuration
            >>> PackageConfig.add_config(
            ...     pkg_name="my_package",
            ...     python_version="3.11",
            ...     pkg_version_min="1.2.0",
            ...     pkg_version_max="2.0.2",
            ... )
            >>> # Overwrite existing configuration
            >>> PackageConfig.add_config(
            ...     pkg_name="my_package",
            ...     python_version="3.11",
            ...     pkg_version_min="1.3.0",
            ...     pkg_version_max="2.1.0",
            ...     exist_ok=True,
            ... )

            ```
        """
        cls.registry[pkg_name] = cls.registry.get(pkg_name, {})

        if python_version in cls.registry[pkg_name] and not exist_ok:
            msg = (
                f"A package configuration ({cls.registry[pkg_name][python_version]}) is "
                f"already registered for package {pkg_name} and python {python_version}. "
                f"Please use `exist_ok=True` if you want to overwrite the package config"
            )
            raise RuntimeError(msg)

        cls.registry[pkg_name][python_version] = {
            "min": pkg_version_min,
            "max": pkg_version_max,
        }

    @classmethod
    def get_config(cls, pkg_name: str, python_version: str) -> dict[str, str | None]:
        r"""Get the package version configuration for a package and
        Python version.

        Retrieves the minimum and maximum version constraints for a package
        on the specified Python version from the registry.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            A dictionary with ``"min"`` and ``"max"`` keys containing the
            version constraint strings, or ``None`` for no constraint. Returns
            an empty dictionary if no configuration exists for the package or
            Python version.

        Example:
            ```pycon
            >>> from feu.package import PackageConfig
            >>> # Get configuration for an existing package
            >>> PackageConfig.get_config(pkg_name="numpy", python_version="3.11")
            {'min': '1.23.2', 'max': None}
            >>> # Query a non-existent configuration
            >>> PackageConfig.get_config(pkg_name="unknown_pkg", python_version="3.11")
            {}

            ```
        """
        if pkg_name not in cls.registry:
            return {}
        return cls.registry[pkg_name].get(python_version, {})

    @classmethod
    def get_min_and_max_versions(
        cls, pkg_name: str, python_version: str
    ) -> tuple[Version | None, Version | None]:
        r"""Get the minimum and maximum versions as Version objects.

        Retrieves the version constraints for a package and Python version,
        converting them from strings to ``packaging.version.Version`` objects
        for comparison operations.

        Args:
            pkg_name: The package name to query (e.g., ``"numpy"``).
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            A tuple ``(min_version, max_version)`` where each value is either
            a ``packaging.version.Version`` object or ``None``. Returns
            ``(None, None)`` if no configuration exists for the package or
            Python version.

        Example:
            ```pycon
            >>> from feu.package import PackageConfig
            >>> PackageConfig.get_min_and_max_versions(
            ...     pkg_name="numpy",
            ...     python_version="3.11",
            ... )
            (<Version('1.23.2')>, None)

            ```
        """
        config = cls.get_config(pkg_name=pkg_name, python_version=python_version)
        min_version = config.get("min", None)
        max_version = config.get("max", None)
        if min_version is not None:
            min_version = Version(min_version)
        if max_version is not None:
            max_version = Version(max_version)
        return min_version, max_version

    @classmethod
    def find_closest_version(cls, pkg_name: str, pkg_version: str, python_version: str) -> str:
        r"""Find the closest valid version for a package.

        Given a requested package version, this method returns the closest
        valid version based on the configured constraints for the package
        and Python version. The logic is:

        - If the requested version is below the minimum, return the minimum version
        - If the requested version is above the maximum, return the maximum version
        - Otherwise, return the requested version unchanged

        If no configuration exists for the package or Python version, the
        requested version is returned unchanged.

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The requested package version to validate.
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            The closest valid version as a string. This will be either the
            requested version (if valid), the minimum version (if too low),
            or the maximum version (if too high).

        Example:
            ```pycon
            >>> from feu.package import PackageConfig
            >>> # Valid version is returned unchanged
            >>> PackageConfig.find_closest_version(
            ...     pkg_name="numpy",
            ...     pkg_version="2.0.2",
            ...     python_version="3.11",
            ... )
            '2.0.2'
            >>> # Version too low, returns minimum
            >>> PackageConfig.find_closest_version(
            ...     pkg_name="numpy",
            ...     pkg_version="1.0.2",
            ...     python_version="3.11",
            ... )
            '1.23.2'

            ```
        """
        version = Version(pkg_version)
        min_version, max_version = cls.get_min_and_max_versions(
            pkg_name=pkg_name, python_version=python_version
        )
        if min_version is not None and version < min_version:
            return min_version.base_version
        if max_version is not None and version > max_version:
            return max_version.base_version
        return pkg_version

    @classmethod
    def is_valid_version(cls, pkg_name: str, pkg_version: str, python_version: str) -> bool:
        r"""Check if a package version is valid for a Python version.

        Validates whether the specified package version falls within the
        configured minimum and maximum version constraints for the given
        Python version.

        If no configuration exists for the package or Python version, the
        version is considered valid (returns ``True``).

        Args:
            pkg_name: The package name to check (e.g., ``"numpy"``).
            pkg_version: The package version to validate.
            python_version: The Python version (e.g., ``"3.11"``).

        Returns:
            ``True`` if the package version is valid for the Python version
            (i.e., it meets the minimum and maximum version constraints),
            ``False`` otherwise. Returns ``True`` if no configuration exists.

        Example:
            ```pycon
            >>> from feu.package import PackageConfig
            >>> # Valid version
            >>> PackageConfig.is_valid_version(
            ...     pkg_name="numpy",
            ...     pkg_version="2.0.2",
            ...     python_version="3.11",
            ... )
            True
            >>> # Version too low
            >>> PackageConfig.is_valid_version(
            ...     pkg_name="numpy",
            ...     pkg_version="1.0.2",
            ...     python_version="3.11",
            ... )
            False

            ```
        """
        version = Version(pkg_version)

        min_version, max_version = cls.get_min_and_max_versions(
            pkg_name=pkg_name,
            python_version=python_version,
        )

        valid = True
        if min_version is not None:
            valid &= min_version <= version
        if max_version is not None:
            valid &= version <= max_version
        return valid


def find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> str:
    r"""Find the closest valid version for a package.

    This is a convenience function that delegates to
    ``PackageConfig.find_closest_version``. See that method for full
    documentation.

    Given a requested package version, returns the closest valid version
    based on the configured constraints:

    - If the requested version is below the minimum, return the minimum version
    - If the requested version is above the maximum, return the maximum version
    - Otherwise, return the requested version unchanged

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The requested package version to validate.
        python_version: The Python version (e.g., ``"3.11"``).

    Returns:
        The closest valid version as a string.

    Example:
        ```pycon
        >>> from feu.package import find_closest_version
        >>> # Valid version is returned unchanged
        >>> find_closest_version(
        ...     pkg_name="numpy",
        ...     pkg_version="2.0.2",
        ...     python_version="3.11",
        ... )
        '2.0.2'
        >>> # Version too low, returns minimum
        >>> find_closest_version(
        ...     pkg_name="numpy",
        ...     pkg_version="1.0.2",
        ...     python_version="3.11",
        ... )
        '1.23.2'

        ```
    """
    return PackageConfig.find_closest_version(
        pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
    )


def is_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> bool:
    r"""Check if a package version is valid for a Python version.

    This is a convenience function that delegates to
    ``PackageConfig.is_valid_version``. See that method for full
    documentation.

    Validates whether the specified package version falls within the
    configured minimum and maximum version constraints.

    Args:
        pkg_name: The package name to check (e.g., ``"numpy"``).
        pkg_version: The package version to validate.
        python_version: The Python version (e.g., ``"3.11"``).

    Returns:
        ``True`` if the package version is valid for the Python version,
        ``False`` otherwise. Returns ``True`` if no configuration exists.

    Example:
        ```pycon
        >>> from feu.package import is_valid_version
        >>> # Valid version
        >>> is_valid_version(
        ...     pkg_name="numpy",
        ...     pkg_version="2.0.2",
        ...     python_version="3.11",
        ... )
        True
        >>> # Version too low
        >>> is_valid_version(
        ...     pkg_name="numpy",
        ...     pkg_version="1.0.2",
        ...     python_version="3.11",
        ... )
        False

        ```
    """
    return PackageConfig.is_valid_version(
        pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
    )
