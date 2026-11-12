from __future__ import annotations

import pytest

from feu import is_package_available
from feu.compat import Target, find_closest_version
from feu.imports import clear_availability_caches
from feu.install import (
    InstallerSpec,
    PipInstaller,
    UvInstaller,
    install_package,
    install_package_closest_version,
)
from feu.testing import pip_available, uv_available
from feu.utils.package import PackageSpec
from feu.utils.platform import get_python_version


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    clear_availability_caches()


@pytest.fixture(scope="module")
def pkg_name() -> str:
    return "cowsay"


@pytest.fixture(scope="module")
def pkg_version(pkg_name: str) -> str:
    return find_closest_version(
        pkg_name=pkg_name,
        pkg_version="6.1",
        target=Target(python_version=get_python_version()),
    )


#####################################
#     Tests for install_package     #
#####################################


@pip_available
def test_install_package_pip(pkg_name: str, pkg_version: str) -> None:
    """Test that a package is installed with pip."""
    install_package(
        installer=InstallerSpec("pip"), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


@uv_available
def test_install_package_uv(pkg_name: str, pkg_version: str) -> None:
    """Test that a package is installed with uv."""
    install_package(
        installer=InstallerSpec("uv"), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


#####################################################
#     Tests for install_package_closest_version     #
#####################################################


@pip_available
def test_install_package_closest_version_pip(pkg_name: str, pkg_version: str) -> None:
    """Test that the closest version of a package is installed with
    pip."""
    install_package_closest_version(
        installer=InstallerSpec("pip"), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


@uv_available
def test_install_package_closest_version_uv(pkg_name: str, pkg_version: str) -> None:
    """Test that the closest version of a package is installed with
    uv."""
    install_package_closest_version(
        installer=InstallerSpec("uv"), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


#################################
#     Tests for the installers  #
#################################


@pip_available
def test_pip_installer(pkg_name: str, pkg_version: str) -> None:
    """Test that the pip installer installs a package."""
    PipInstaller().install(PackageSpec(name=pkg_name, version=pkg_version))
    assert is_package_available(pkg_name)


@uv_available
def test_uv_installer(pkg_name: str, pkg_version: str) -> None:
    """Test that the uv installer installs a package."""
    UvInstaller().install(PackageSpec(name=pkg_name, version=pkg_version))
    assert is_package_available(pkg_name)
