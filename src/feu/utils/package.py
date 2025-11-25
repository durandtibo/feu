r"""Contain utility functions to manage packages."""

from __future__ import annotations

__all__ = [
    "PackageDependency",
    "PackageSpec",
    "extract_package_extras",
    "extract_package_name",
    "generate_extras_string",
]

import copy
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class PackageSpec:
    r"""Define a dataclass to represent a package specification.

    Args:
        name: The package name.
        version: An optional package version.
        extras: Optional package extra dependencies.

    Example usage:

    ```pycon

    >>> from feu.utils.package import PackageSpec
    >>> pkg1 = PackageSpec("my_package")
    >>> pkg1
    PackageSpec(name='my_package', version=None, extras=None)
    >>> pkg2 = PackageSpec("my_package", version="1.2.3")
    >>> pkg2
    PackageSpec(name='my_package', version='1.2.3', extras=None)
    >>> pkg3 = PackageSpec("my_package", version="1.2.3", extras=["security", "socks"])
    >>> pkg3
    PackageSpec(name='my_package', version='1.2.3', extras=['security', 'socks'])

    ```
    """

    name: str
    version: str | None = field(default=None)
    extras: list[str] | None = field(default=None)

    def __str__(self) -> str:
        extras_str = generate_extras_string(self.extras) if self.extras else ""
        version_str = f"=={self.version}" if self.version else ""
        return f"{self.name}{extras_str}{version_str}"

    def to_package_dependency(self) -> PackageDependency:
        r"""Convert to a ``PackageDependency``.

        Returns:
            The current package as a package dependency.

        Example usage:

        ```pycon

        >>> from feu.utils.package import PackageSpec
        >>> pkg = PackageSpec("my_package")
        >>> dep = pkg.to_package_dependency()
        >>> dep
        PackageDependency(name='my_package', version_specifiers=None, extras=None)

        ```
        """
        return PackageDependency(
            name=self.name,
            extras=self.extras,
            version_specifiers=[f"=={self.version}"] if self.version else None,
        )

    def with_version(self, version: str | None) -> PackageSpec:
        r"""Create a new ``PackageSpec`` instance with the given version.

        Args:
            version: The new version to apply.

        Returns:
            A new instance of PackageSpec with the updated version.

        Example usage:

        ```pycon

        >>> from feu.utils.package import PackageSpec
        >>> pkg = PackageSpec("my_package", version="1.2.0")
        >>> pkg
        PackageSpec(name='my_package', version='1.2.0', extras=None)
        >>> pkg2 = pkg.with_version("1.2.3")
        >>> pkg2
        PackageSpec(name='my_package', version='1.2.3', extras=None)

        ```
        """
        return self.__class__(name=self.name, version=version, extras=copy.deepcopy(self.extras))


@dataclass
class PackageDependency:
    r"""Define a dataclass to represent a package dependency.

    Args:
        name: The package name.
        version_specifiers: Optional package version specifies.
        extras: Optional package extra dependencies.

    Example usage:

    ```pycon

    >>> from feu.utils.package import PackageDependency
    >>> pkg1 = PackageDependency("my_package")
    >>> pkg1
    PackageDependency(name='my_package', version_specifiers=None, extras=None)
    >>> pkg2 = PackageDependency("my_package", version_specifiers=["==1.2.3"])
    >>> pkg2
    PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=None)
    >>> pkg3 = PackageDependency(
    ...     "my_package", version_specifiers=["==1.2.3"], extras=["security", "socks"]
    ... )
    >>> pkg3
    PackageDependency(name='my_package', version_specifiers=['==1.2.3'], extras=['security', 'socks'])

    ```
    """

    name: str
    version_specifiers: list[str] | None = field(default=None)
    extras: list[str] | None = field(default=None)

    def __str__(self) -> str:
        extras_str = generate_extras_string(self.extras) if self.extras else ""
        version_str = ",".join(self.version_specifiers) if self.version_specifiers else ""
        return f"{self.name}{extras_str}{version_str}"


def extract_package_name(requirement: str) -> str:
    r"""Extract the base package name from a requirement string.

    The requirement string may include optional dependencies in square brackets,
    such as 'package[extra1,extra2]'. This function returns only the base package
    name without the extras.

    Args:
        requirement: The requirement string containing the package name and
            optionally extra dependencies.

    Returns:
        The base package name without extras.

    Example usage:

    ```pycon

    >>> from feu.utils.package import extract_package_name
    >>> extract_package_name("numpy")
    'numpy'
    >>> extract_package_name("pandas[performance]")
    'pandas'
    >>> extract_package_name("requests[security,socks]")
    'requests'

    ```
    """
    match = re.match(r"^([a-zA-Z0-9_\-\.]+)", requirement)
    return match.group(1) if match else requirement


def extract_package_extras(requirement: str) -> list[str]:
    r"""Extract the optional extras from a requirement string.

    The requirement string may include extras in square brackets, e.g.,
    'package[extra1,extra2]'. This function returns the list of extras.

    Args:
        requirement: The requirement string containing the package name and
            optionally extra dependencies.

    Returns:
        A list of extra requirements, or an empty list if none exist.

    Example usage:

    ```pycon

    >>> from feu.utils.package import extract_package_extras
    >>> extract_package_extras("numpy")
    []
    >>> extract_package_extras("pandas[performance]")
    ['performance']
    >>> extract_package_extras("requests[security,socks]")
    ['security', 'socks']

    ```
    """
    match = re.search(r"\[([^\]]+)\]", requirement)
    if not match:
        return []
    return [extra.strip() for extra in match.group(1).split(",")]


def generate_extras_string(extras: Sequence[str]) -> str:
    r"""Generate a string with the package extras i.e. optional
    dependencies.

    Args:
        extras: The package optional dependencies.

    Returns:
        A string with the package extras.

    Example usage:

    ```pycon

    >>> from feu.utils.package import generate_extras_string
    >>> generate_extras_string(["security"])
    '[security]'
    >>> generate_extras_string(["security", "socks"])
    '[security,socks]'
    >>> generate_extras_string([])
    ''

    ```
    """
    if not extras:
        return ""
    return f"[{','.join(extras)}]"
