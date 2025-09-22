__all__ = ["PipInstaller"]

from typing import ClassVar

from feu.installer.installer import BaseInstaller
from feu.installer.pip.command import PipCommandGenerator
from feu.installer.pip.package import (
    BasePackageInstaller,
    PackageInstaller,
    create_package_installer_mapping,
)
from feu.installer.pip.resolver import DependencyResolver


class PipInstaller(BaseInstaller):
    """Implement a pip package installer."""

    registry: ClassVar[dict[str, BasePackageInstaller]] = create_package_installer_mapping(
        command=PipCommandGenerator()
    )

    @classmethod
    def add_installer(
        cls, package: str, installer: BasePackageInstaller, exist_ok: bool = False
    ) -> None:
        r"""Add an installer for a given package.

        Args:
            package: The package name.
            installer: The installer used for the given package.
            exist_ok: If ``False``, ``RuntimeError`` is raised if the
                package already exists. This parameter should be set
                to ``True`` to overwrite the installer for a package.

        Raises:
            RuntimeError: if an installer is already registered for the
                package name and ``exist_ok=False``.

        Example usage:

        ```pycon

        >>> from feu.installer.pip import (
        ...     PipInstaller,
        ...     PandasDependencyResolver,
        ...     PipCommandGenerator,
        ... )
        >>> PipInstaller.add_installer(
        ...     "pandas",
        ...     PackageInstaller(
        ...         resolver=PandasDependencyResolver(), command=PipCommandGenerator()
        ...     ),
        ...     exist_ok=True,
        ... )

        ```
        """
        if package in cls.registry and not exist_ok:
            msg = (
                f"An installer ({cls.registry[package]}) is already registered for the data "
                f"type {package}. Please use `exist_ok=True` if you want to overwrite the "
                "installer for this type"
            )
            raise RuntimeError(msg)
        cls.registry[package] = installer

    @classmethod
    def has_installer(cls, package: str) -> bool:
        r"""Indicate if an installer is registered for the given package.

        Args:
            package: The package name.

        Returns:
            ``True`` if an installer is registered,
                otherwise ``False``.

        Example usage:

        ```pycon

        >>> from feu.installer.pip import PipInstaller
        >>> PipInstaller.has_installer("pandas")

        ```
        """
        return package in cls.registry

    @classmethod
    def install(cls, package: str, version: str, args: str = "") -> None:
        installer = cls.registry.get(package, None)
        if installer is None:
            installer = PackageInstaller(
                resolver=DependencyResolver(package), command=PipCommandGenerator()
            )
        installer.install(version=version, args=args)
