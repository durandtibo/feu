r"""Contain utility functions to install packages."""

from __future__ import annotations

__all__ = [
    "BaseInstaller",
    "DefaultInstaller",
    "PackageInstaller",
    "PandasInstaller",
    "TorchInstaller",
    "XarrayInstaller",
    "install_package",
    "run_bash_command",
]

import logging
import subprocess
from abc import ABC, abstractmethod
from typing import ClassVar

from packaging.version import Version

logger = logging.getLogger(__name__)


def run_bash_command(cmd: str) -> None:
    r"""Execute a bash command.

    Args:
        cmd: The command to run.
    """
    logger.info(f"execute the following command: {cmd}")
    subprocess.run(cmd.split(), check=True)  # noqa: S603


class BaseInstaller(ABC):
    r"""Define the base class to implement a package installer."""

    @abstractmethod
    def install(self, version: str) -> None:
        r"""Install the given package version.

        Args:
            version: The target version to install.
        """


class DefaultInstaller(BaseInstaller):
    r"""Implement a generic package installer.

    Args:
        package: The name of the package to install.
    """

    def __init__(self, package: str) -> None:
        self._package = package

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(package={self._package})"

    def install(self, version: str) -> None:
        run_bash_command(f"pip install -U {self._package}=={version}")


class PandasInstaller(BaseInstaller):
    r"""Implement the ``pandas`` package installer.

    ``numpy`` 2.0 support was added in ``pandas`` 2.2.2.
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def install(self, version: str) -> None:
        deps = "" if Version(version) >= Version("2.2.2") else " numpy==1.26.4"
        run_bash_command(f"pip install -U pandas=={version}{deps}")


class TorchInstaller(BaseInstaller):
    r"""Implement the ``torch`` package installer.

    ``numpy`` 2.0 support was added in ``torch`` 2.3.0.
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def install(self, version: str) -> None:
        deps = "" if Version(version) >= Version("2.3.0") else " numpy==1.26.4"
        run_bash_command(f"pip install -U torch=={version}{deps}")


class XarrayInstaller(BaseInstaller):
    r"""Implement the ``xarray`` package installer.

    ``numpy`` 2.0 support was added in ``xarray`` 2023.9.
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def install(self, version: str) -> None:
        deps = "" if Version(version) >= Version("2023.9") else " numpy==1.26.4"
        run_bash_command(f"pip install -U xarray=={version}{deps}")


class PackageInstaller:
    """Implement the default equality tester."""

    registry: ClassVar[dict[str, BaseInstaller]] = {
        "pandas": PandasInstaller(),
        "torch": TorchInstaller(),
        "xarray": XarrayInstaller(),
    }

    @classmethod
    def add_installer(cls, package: str, installer: BaseInstaller, exist_ok: bool = False) -> None:
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


def install_package(package: str, version: str) -> None:
    r"""Install a package and associated packages.

    Args:
        package: The package name e.g. ``'pandas'``.
        version: The target version to install.

    Example usage:

    ```pycon

    >>> from feu import install_package
    >>> install_package("pandas", "2.2.2")  # doctest: +SKIP

    ```
    """
    PackageInstaller.install(package, version)
