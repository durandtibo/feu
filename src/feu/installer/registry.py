from typing import ClassVar

from feu.installer.installer import BaseInstaller


class InstallerRegistry:
    """Implement the main installer."""

    registry: ClassVar[dict[str, BaseInstaller]] = {
        "pip": PipInstaller(),
        "pipx": PipInstaller(),
        "uv": PipInstaller(),
    }

    @classmethod
    def add_installer(cls, name: str, installer: BaseInstaller, exist_ok: bool = False) -> None:
        r"""Add an installer for a given package.

        Args:
            name: The installer name e.g. pip or uv.
            installer: The installer used for the given package.
            exist_ok: If ``False``, ``RuntimeError`` is raised if the
                package already exists. This parameter should be set
                to ``True`` to overwrite the installer for a package.

        Raises:
            RuntimeError: if an installer is already registered for the
                package name and ``exist_ok=False``.

        Example usage:

        ```pycon

        >>> from feu.installer import Installer, PipInstaller
        >>> PackageInstaller.add_installer("pandas", PandasInstaller(), exist_ok=True)

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
    def install(cls, installer: str, package: str, version: str, args: str = "") -> None:
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
        cls.registry[installer].install(package=package, version=version, args=args)
