r"""Contain utility functions to install packages."""

from __future__ import annotations

__all__ = [
    "BaseInstaller",
    "DefaultInstaller",
    "JaxInstaller",
    "MatplotlibInstaller",
    "Numpy2Installer",
    "PackageInstaller",
    "PandasInstaller",
    "PyarrowInstaller",
    "SklearnInstaller",
    "ScipyInstaller",
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


class Numpy2Installer(BaseInstaller):
    r"""Define a package installer to install package that did not pin
    ``numpy<2.0`` and are not fully compatible with numpy.

    https://github.com/numpy/numpy/issues/26191 indicates the packages
    that are compatible with numpy 2.0.

    Args:
        package: The name of the package to install.
        min_version: The first version that is fully compatible with
            numpy 2.0.
    """

    def __init__(self, package: str, min_version: str) -> None:
        self._package = package
        self._min_version = min_version

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def install(self, version: str) -> None:
        deps = "" if Version(version) >= Version(self._min_version) else " numpy<2.0.0"
        run_bash_command(f"pip install -U {self._package}=={version}{deps}")


class JaxInstaller(BaseInstaller):
    r"""Implement the ``jax`` package installer.

    ``numpy`` 2.0 support was added in ``jax`` 0.4.26.
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def install(self, version: str) -> None:
        ver = Version(version)
        deps = "" if ver >= Version("0.4.26") else " numpy<2.0.0"
        if (Version("0.4.9") <= ver) and (ver <= Version("0.4.11")):
            # https://github.com/google/jax/issues/17693
            deps += " ml_dtypes<=0.2.0"
        run_bash_command(f"pip install -U jax=={version} jaxlib=={version}{deps}")


class MatplotlibInstaller(Numpy2Installer):
    r"""Implement the ``matplotlib`` package installer.

    ``numpy`` 2.0 support was added in ``matplotlib`` 3.8.4.
    """

    def __init__(self) -> None:
        super().__init__(package="matplotlib", min_version="3.8.4")


class PandasInstaller(Numpy2Installer):
    r"""Implement the ``pandas`` package installer.

    ``numpy`` 2.0 support was added in ``pandas`` 2.2.2.
    """

    def __init__(self) -> None:
        super().__init__(package="pandas", min_version="2.2.2")


class PyarrowInstaller(Numpy2Installer):
    r"""Implement the ``pyarrow`` package installer.

    ``numpy`` 2.0 support was added in ``pyarrow`` 16.0.
    """

    def __init__(self) -> None:
        super().__init__(package="pyarrow", min_version="16.0")


class ScipyInstaller(Numpy2Installer):
    r"""Implement the ``scipy`` package installer.

    ``numpy`` 2.0 support was added in ``scipy`` 1.13.0.
    """

    def __init__(self) -> None:
        super().__init__(package="scipy", min_version="1.13.0")


class SklearnInstaller(Numpy2Installer):
    r"""Implement the ``sklearn`` package installer.

    ``numpy`` 2.0 support was added in ``sklearn`` 1.4.2.
    """

    def __init__(self) -> None:
        super().__init__(package="scikit-learn", min_version="1.4.2")


class TorchInstaller(Numpy2Installer):
    r"""Implement the ``torch`` package installer.

    ``numpy`` 2.0 support was added in ``torch`` 2.3.0.
    """

    def __init__(self) -> None:
        super().__init__(package="torch", min_version="2.3.0")


class XarrayInstaller(Numpy2Installer):
    r"""Implement the ``xarray`` package installer.

    ``numpy`` 2.0 support was added in ``xarray`` 2024.6.0.
    """

    def __init__(self) -> None:
        super().__init__(package="xarray", min_version="2024.6.0")


class PackageInstaller:
    """Implement the main package installer."""

    registry: ClassVar[dict[str, BaseInstaller]] = {
        "jax": JaxInstaller(),
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
