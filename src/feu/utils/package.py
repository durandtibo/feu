r"""Contain utility functions to manage packages."""

from __future__ import annotations

__all__ = ["PackageSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING

from packaging.requirements import Requirement

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True, init=False)
class PackageSpec:
    r"""Define a dataclass to represent a package specification.

    Args:
        name: The package name.
        version: The package version request: an exact version
            (``"2.4.0"``), a wildcard (``"2.4.*"``) or ``""``/``None``
            for the latest version. The string representation pins the
            version with ``==`` unless the request is the latest
            version. ``None`` is stored as ``""``.
        extras: Optional package extra dependencies. A list is stored
            as a tuple.

    Example:
        ```pycon
        >>> from feu.utils.package import PackageSpec
        >>> pkg1 = PackageSpec("my_package")
        >>> pkg1
        PackageSpec(name='my_package', version='', extras=())
        >>> str(pkg1)
        'my_package'
        >>> pkg2 = PackageSpec("my_package", version="1.2.3")
        >>> pkg2
        PackageSpec(name='my_package', version='1.2.3', extras=())
        >>> str(pkg2)
        'my_package==1.2.3'
        >>> pkg3 = PackageSpec("my_package", version="1.*", extras=["security", "socks"])
        >>> pkg3
        PackageSpec(name='my_package', version='1.*', extras=('security', 'socks'))
        >>> str(pkg3)
        'my_package[security,socks]==1.*'

        ```
    """

    name: str
    version: str
    extras: tuple[str, ...]

    def __init__(
        self, name: str, version: str | None = "", extras: Sequence[str] | None = ()
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version or "")
        object.__setattr__(self, "extras", tuple(extras or ()))

    def __str__(self) -> str:
        extras_str = f"[{','.join(self.extras)}]" if self.extras else ""
        version_str = f"=={self.version}" if self.version else ""
        return f"{self.name}{extras_str}{version_str}"

    def to_requirement(self) -> Requirement:
        r"""Convert to a ``packaging.requirements.Requirement``.

        Returns:
            The current package as a requirement.

        Example:
            ```pycon
            >>> from feu.utils.package import PackageSpec
            >>> PackageSpec("my_package", version="1.2.*").to_requirement()
            <Requirement('my_package==1.2.*')>

            ```
        """
        return Requirement(str(self))

    def with_version(self, version: str | None) -> PackageSpec:
        r"""Create a new ``PackageSpec`` instance with the given version.

        Args:
            version: The new version request to apply.

        Returns:
            A new instance of PackageSpec with the updated version.

        Example:
            ```pycon
            >>> from feu.utils.package import PackageSpec
            >>> pkg = PackageSpec("my_package", version="1.2.0")
            >>> pkg
            PackageSpec(name='my_package', version='1.2.0', extras=())
            >>> pkg2 = pkg.with_version("1.2.3")
            >>> pkg2
            PackageSpec(name='my_package', version='1.2.3', extras=())

            ```
        """
        return self.__class__(name=self.name, version=version, extras=self.extras)
