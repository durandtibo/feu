from __future__ import annotations

import pytest

from feu import install_package, is_package_available
from feu.install import PackageInstaller

PACKAGES = [
    # ("jax", "0.4.30"),
    ("matplotlib", "3.9.0"),
    ("numpy", "2.0.0"),
    ("pandas", "2.2.2"),
    ("sklearn", "1.4.2"),
    # ("torch", "2.2.2"),
    ("xarray", "2024.6"),
]


#####################################
#     Tests for install_package     #
#####################################


@pytest.mark.parametrize(("package", "version"), PACKAGES)
def test_install_package(package: str, version: str) -> None:
    install_package(package=package, version=version)
    assert is_package_available(package)


######################################
#     Tests for PackageInstaller     #
######################################


@pytest.mark.parametrize(("package", "version"), PACKAGES)
def test_package_installer_install(package: str, version: str) -> None:
    PackageInstaller.install(package=package, version=version)
    assert is_package_available(package)
