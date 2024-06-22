from __future__ import annotations

from feu import install_package, is_package_available
from feu.install import (
    DefaultInstaller,
    PackageInstaller,
    PandasInstaller,
    TorchInstaller,
    XarrayInstaller,
)

######################################
#     Tests for DefaultInstaller     #
######################################


def test_default_installer_install() -> None:
    DefaultInstaller("numpy").install("2.0.0")
    assert is_package_available("numpy")


#####################################
#     Tests for PandasInstaller     #
#####################################


def test_pandas_installer_install() -> None:
    PandasInstaller().install("2.2.2")
    assert is_package_available("pandas")


####################################
#     Tests for TorchInstaller     #
####################################


def test_torch_installer_install() -> None:
    TorchInstaller().install("2.3.1")
    assert is_package_available("torch")


#####################################
#     Tests for XarrayInstaller     #
#####################################


def test_xarray_installer_install() -> None:
    XarrayInstaller().install("2024.6")
    assert is_package_available("xarray")


#####################################
#     Tests for install_package     #
#####################################


def test_install_package() -> None:
    install_package(package="numpy", version="2.0.0")
    assert is_package_available("numpy")


######################################
#     Tests for PackageInstaller     #
######################################


def test_package_installer_install_numpy() -> None:
    PackageInstaller.install(package="numpy", version="2.0.0")
    assert is_package_available("numpy")
