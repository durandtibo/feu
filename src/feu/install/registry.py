r"""Contain the main installer registry."""

from __future__ import annotations

__all__ = ["InstallerRegistry"]

from typing import TYPE_CHECKING, ClassVar

from feu.install.pip import PipInstaller, PipxInstaller, UvInstaller

if TYPE_CHECKING:
    from feu.install.installer import BaseInstaller
    from feu.utils.installer import InstallerSpec
    from feu.utils.package import PackageSpec


class InstallerRegistry:
    r"""Implement the main installer registry."""

    registry: ClassVar[dict[str, type[BaseInstaller]]] = {
        "pip": PipInstaller,
        "pipx": PipxInstaller,
        "uv": UvInstaller,
    }

    @classmethod
    def add_installer(
        cls, name: str, installer: type[BaseInstaller], exist_ok: bool = False
    ) -> None:
        r"""Add an installer for a given package.

        Args:
            name: The installer name e.g. pip or uv.
            installer: The installer used for the given package.
            exist_ok: If ``False``, ``RuntimeError`` is raised if the
                installer already exists. This parameter should be set
                to ``True`` to overwrite the installer for a package.

        Raises:
            RuntimeError: if an installer is already registered for the
                package name and ``exist_ok=False``.

        Example usage:

        ```pycon

        >>> from feu.install import InstallerRegistry
        >>> from feu.install.pip import PipInstaller
        >>> InstallerRegistry.add_installer("pip", PipInstaller, exist_ok=True)

        ```
        """
        if name in cls.registry and not exist_ok:
            msg = (
                f"An installer ({cls.registry[name]}) is already registered for the name "
                f"{name}. Please use `exist_ok=True` if you want to overwrite the "
                "installer for this name"
            )
            raise RuntimeError(msg)
        cls.registry[name] = installer

    @classmethod
    def has_installer(cls, name: str) -> bool:
        r"""Indicate if an installer is registered for the given name.

        Args:
            name: The installer name.

        Returns:
            ``True`` if an installer is registered,
                otherwise ``False``.

        Example usage:

        ```pycon

        >>> from feu.install import InstallerRegistry
        >>> InstallerRegistry.has_installer("pip")
        True

        ```
        """
        return name in cls.registry

    @classmethod
    def install(cls, installer: InstallerSpec, package: PackageSpec) -> None:
        r"""Install a package and associated packages by using the
        specified installer.

        Args:
            installer: The installer specification.
            package: The package specification.

        Example usage:

        ```pycon

        >>> from feu.install import InstallerRegistry
        >>> from feu.utils.installer import InstallerSpec
        >>> from feu.utils.package import PackageSpec
        >>> InstallerRegistry.install(
        ...     installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.2.2")
        ... )  # doctest: +SKIP

        ```
        """
        cls.registry[installer.name].instantiate_with_arguments(installer.arguments).install(
            package=package
        )
