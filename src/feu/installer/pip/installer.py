__all__ = ["PipInstaller"]

from typing import ClassVar

from feu.installer.installer import BaseInstaller
from feu.installer.pip.command import PipCommandGenerator
from feu.installer.pip.package import BasePackageInstaller, PackageInstaller
from feu.installer.pip.resolver import JaxDependencyResolver


class PipInstaller(BaseInstaller):
    """Implement a pip package installer."""

    registry: ClassVar[dict[str, BasePackageInstaller]] = {
        "jax": PackageInstaller(resolver=JaxDependencyResolver(), command=PipCommandGenerator()),
        "matplotlib": MatplotlibInstaller(),
        "pandas": PandasInstaller(),
        "pyarrow": PyarrowInstaller(),
        "scikit-learn": SklearnInstaller(),
        "scipy": ScipyInstaller(),
        "sklearn": SklearnInstaller(),
        "torch": TorchInstaller(),
        "xarray": XarrayInstaller(),
    }

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

        >>> from feu.install import PackageInstaller, PandasInstaller
        >>> PackageInstaller.add_installer("pandas", PandasInstaller(), exist_ok=True)

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

        >>> from feu.install import PackageInstaller
        >>> PackageInstaller.has_installer("pandas")

        ```
        """
        return package in cls.registry

    @classmethod
    def install(cls, package: str, version: str) -> None:
        r"""Install a package and associated packages.

        Args:
            package: The package name e.g. ``'pandas'``.
            version: The target version to install.

        Example usage:

        ```pycon

        >>> from feu.install import PackageInstaller
        >>> PackageInstaller().install("pandas", "2.2.2")  # doctest: +SKIP

        ```
        """
        cls.registry.get(package, DefaultInstaller(package)).install(version)
