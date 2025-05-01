from __future__ import annotations

from sys import version_info

import pytest

from feu import install_package, is_package_available
from feu.install import PackageInstaller
from feu.package import find_closest_version

PACKAGES = [
    ("numpy", "2.2.5"),
    ("pandas", "2.2.3"),
    ("sklearn", "1.6.0"),
    ("torch", "2.7.0"),
    ("xarray", "2024.9"),
]


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture
def python_version() -> str:
    return f"{version_info.major}.{version_info.minor}"


#####################################
#     Tests for install_package     #
#####################################


@pytest.mark.parametrize(("package", "version"), PACKAGES)
def test_install_package(package: str, version: str, python_version: str) -> None:
    version = find_closest_version(
        pkg_name=package, pkg_version=version, python_version=python_version
    )
    install_package(package=package, version=version)
    assert is_package_available(package)


######################################
#     Tests for PackageInstaller     #
######################################


@pytest.mark.parametrize(("package", "version"), PACKAGES)
def test_package_installer_install(package: str, version: str, python_version: str) -> None:
    version = find_closest_version(
        pkg_name=package, pkg_version=version, python_version=python_version
    )
    PackageInstaller.install(package=package, version=version)
    assert is_package_available(package)
