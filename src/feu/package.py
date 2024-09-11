r"""Contain functions to check if a package configuration is valid."""

from __future__ import annotations

__all__ = ["PackageValidator"]

import logging
from typing import ClassVar

logger = logging.getLogger(__name__)


class PackageValidator:
    """Implement the main package validator."""

    registry: ClassVar[dict[str, dict[str, dict[str, str]]]] = {
        "numpy": {
            "3.12": {"min": "1.26.0", "max": None},
            "3.11": {"min": "1.23.2", "max": None},
            "3.10": {"min": "1.21.3", "max": None},
            "3.9": {"min": "1.19.3", "max": "2.0.2"},
        }
    }

    @classmethod
    def add_package_config(
        cls,
        pkg_name: str,
        pkg_version_min: str | None,
        pkg_version_max: str | None,
        python_version: str,
        exist_ok: bool = False,
    ) -> None:
        r"""Add a new package configuration.

        Args:
            pkg_name: The package name.
            pkg_version_min: The minimum valid package version for
                this configuration. ``None`` means there is no minimum
                valid package version.
            pkg_version_max: The maximum valid package version for
                this configuration. ``None`` means there is no maximum
                valid package version.
            python_version: The python version.
            exist_ok: If ``False``, ``RuntimeError`` is raised if a
                package configuration already exists. This parameter
                should be  set to ``True`` to overwrite the package
                configuration.

        Raises:
            RuntimeError: if a package configuration is already
                registered and ``exist_ok=False``.

        Example usage:

        ```pycon

        >>> from feu.package import PackageValidator
        >>> PackageValidator.add_package_config(
        ...     pkg_name="numpy",
        ...     python_version="3.11",
        ...     pkg_version_min="1.2.0",
        ...     pkg_version_max="2.0.2",
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
    def get_package_config(cls, pkg_name: str, python_version: str) -> dict[str, str]:
        r"""Get a specific package configuration.

        Args:
            pkg_name: The package name.
            python_version: The python version.

        Example usage:

        ```pycon

        >>> from feu.package import PackageValidator
        >>> PackageValidator.get_package_config(
        ...     pkg_name="numpy",
        ...     python_version="3.11",
        ... )

        ```
        """
        if pkg_name not in cls.registry:
            return {}
        return cls.registry[pkg_name].get(python_version, {})


# def is_valid(package: str, python: str, os: str = "default") -> bool:
#     pass
