r"""Contain functions to check a package configuration."""

from __future__ import annotations

__all__ = ["PackageConfig", "is_valid_version", "find_closest_version"]

import logging
from typing import ClassVar

from packaging.version import Version

logger = logging.getLogger(__name__)


class PackageConfig:
    """Implement the main package config registry."""

    registry: ClassVar[dict[str, dict[str, dict[str, str]]]] = {
        # https://pypi.org/project/jaxlib/#history
        "jax": {
            "3.12": {"min": "0.4.17", "max": None},
            "3.11": {"min": "0.4.6", "max": None},
            "3.10": {"min": "0.4.6", "max": None},
            "3.9": {"min": "0.4.6", "max": "0.4.30"},
        },
        # https://numpy.org/devdocs/release.html
        "numpy": {
            "3.12": {"min": "1.26.0", "max": None},
            "3.11": {"min": "1.23.2", "max": None},
            "3.10": {"min": "1.21.3", "max": None},
            "3.9": {"min": "1.19.3", "max": "2.0.2"},
        },
        # https://github.com/pandas-dev/pandas/releases
        # https://pandas.pydata.org/docs/whatsnew/index.html
        "pandas": {
            "3.12": {"min": "2.1.1", "max": None},
            "3.11": {"min": "1.3.4", "max": None},
            "3.10": {"min": "1.3.3", "max": None},
            "3.9": {"min": None, "max": None},
        },
        # https://arrow.apache.org/release/
        "pyarrow": {
            "3.12": {"min": "14.0.0", "max": None},
            "3.11": {"min": "10.0.1", "max": None},
            "3.10": {"min": "6.0.0", "max": None},
            "3.9": {"min": "3.0.0", "max": "16.1.0"},
        },
        # https://github.com/pytorch/pytorch/releases
        "torch": {
            "3.12": {"min": "2.4.0", "max": None},
            "3.11": {"min": "2.0.0", "max": None},
            "3.10": {"min": "1.11.0", "max": None},
            "3.9": {"min": None, "max": None},
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

        >>> from feu.package import PackageConfig
        >>> PackageConfig.add_config(
        ...     pkg_name="my_package",
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
    def get_config(cls, pkg_name: str, python_version: str) -> dict[str, str]:
        r"""Get a package configuration given the package name and python
        version.

        Args:
            pkg_name: The package name.
            python_version: The python version.

        Returns:
            The package configuration.

        Example usage:

        ```pycon

        >>> from feu.package import PackageConfig
        >>> PackageConfig.get_config(
        ...     pkg_name="numpy",
        ...     python_version="3.11",
        ... )
        {'min': '1.23.2', 'max': None}

        ```
        """
        if pkg_name not in cls.registry:
            return {}
        return cls.registry[pkg_name].get(python_version, {})

    @classmethod
    def get_min_and_max_versions(
        cls, pkg_name: str, python_version: str
    ) -> tuple[Version | None, Version | None]:
        r"""Get the minimum and maximum versions for the given package
        name and python version.

        Args:
            pkg_name: The package name.
            python_version: The python version.

        Returns:
            A tuple with the minimum and maximum versions.
                The version is set to ``None`` if there is no minimum
                or maximum version.

        Example usage:

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
        r"""Find the closest valid version given the package name and
        version, and python version.

        Args:
            pkg_name: The package name.
            pkg_version: The package version to check.
            python_version: The python version.

        Returns:
            The closest valid version.

        Example usage:

        ```pycon

        >>> from feu.package import PackageConfig
        >>> PackageConfig.find_closest_version(
        ...     pkg_name="numpy",
        ...     pkg_version="2.0.2",
        ...     python_version="3.11",
        ... )
        2.0.2
        >>> PackageConfig.find_closest_version(
        ...     pkg_name="numpy",
        ...     pkg_version="1.0.2",
        ...     python_version="3.11",
        ... )
        1.23.2

        ```
        """
        if cls.is_valid_version(
            pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
        ):
            return pkg_version
        min_version, max_version = cls.get_min_and_max_versions(
            pkg_name=pkg_name, python_version=python_version
        )
        version = Version(pkg_version)
        if min_version is not None and version < min_version:
            return min_version.base_version
        return max_version.base_version

    @classmethod
    def is_valid_version(cls, pkg_name: str, pkg_version: str, python_version: str) -> bool:
        r"""Indicate if the specified package version is valid for the
        given Python version.

        Args:
            pkg_name: The package name.
            pkg_version: The package version to check.
            python_version: The python version.

        Returns:
            ``True`` if the specified package version is valid for the
                given Python version, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from feu.package import PackageConfig
        >>> PackageConfig.is_valid_version(
        ...     pkg_name="numpy",
        ...     pkg_version="2.0.2",
        ...     python_version="3.11",
        ... )
        True
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
            pkg_name=pkg_name, python_version=python_version
        )
        if min_version is None and max_version is None:
            return True
        if min_version is None:
            return version <= max_version
        if max_version is None:
            return min_version <= version
        return (min_version <= version) and (version <= max_version)


def find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> str:
    r"""Find the closest valid version given the package name and
    version, and python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version.

    Returns:
        The closest valid version.

    Example usage:

    ```pycon

    >>> from feu.package import find_closest_version
    >>> find_closest_version(
    ...     pkg_name="numpy",
    ...     pkg_version="2.0.2",
    ...     python_version="3.11",
    ... )
    2.0.2
    >>> find_closest_version(
    ...     pkg_name="numpy",
    ...     pkg_version="1.0.2",
    ...     python_version="3.11",
    ... )
    1.23.2

    ```
    """
    return PackageConfig.find_closest_version(
        pkg_name=str(pkg_name), pkg_version=str(pkg_version), python_version=str(python_version)
    )


def is_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> bool:
    r"""Indicate if the specified package version is valid for the given
    Python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version.

    Returns:
        ``True`` if the specified package version is valid for the
            given Python version, otherwise ``False``.

    Example usage:

    ```pycon

    >>> from feu.package import is_valid_version
    >>> is_valid_version(
    ...     pkg_name="numpy",
    ...     pkg_version="2.0.2",
    ...     python_version="3.11",
    ... )
    True
    >>> is_valid_version(
    ...     pkg_name="numpy",
    ...     pkg_version="1.0.2",
    ...     python_version="3.11",
    ... )
    False

    ```
    """
    return PackageConfig.is_valid_version(
        pkg_name=str(pkg_name), pkg_version=str(pkg_version), python_version=str(python_version)
    )


def _find_closest_version(pkg_name: str, pkg_version: str, python_version: str) -> None:
    r"""Print the closest valid version given the package name and
    version, and python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version.
    """
    print(  # noqa: T201
        find_closest_version(
            pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version
        )
    )


def _is_valid_version(pkg_name: str, pkg_version: str, python_version: str) -> None:
    r"""Print if the specified package version is valid for the given
    Python version.

    Args:
        pkg_name: The package name.
        pkg_version: The package version to check.
        python_version: The python version.
    """
    print(  # noqa: T201
        is_valid_version(pkg_name=pkg_name, pkg_version=pkg_version, python_version=python_version)
    )
