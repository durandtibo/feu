from __future__ import annotations

from unittest.mock import patch

from feu.install import (
    DefaultInstaller,
    PackageInstaller,
    PandasInstaller,
    TorchInstaller,
    XarrayInstaller,
    install_package,
    run_bash_command,
)

######################################
#     Tests for run_bash_command     #
######################################


def test_run_bash_command() -> None:
    # check it does not raise an error
    run_bash_command("ls -l")


def test_run_bash_command_mock() -> None:
    with patch("feu.install.subprocess.run") as run_mock:
        run_bash_command("ls -l")
        run_mock.assert_called_once_with(["ls", "-l"], check=True)


######################################
#     Tests for DefaultInstaller     #
######################################


def test_default_installer_install() -> None:
    installer = DefaultInstaller("numpy")
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.0.0")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


#####################################
#     Tests for PandasInstaller     #
#####################################


def test_pandas_installer_install_high() -> None:
    installer = PandasInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.2.2")
        run_mock.assert_called_once_with("pip install -U pandas==2.2.2")


def test_pandas_installer_install_low() -> None:
    installer = PandasInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.1.1")
        run_mock.assert_called_once_with("pip install -U pandas==2.1.1 numpy==1.26.4")


####################################
#     Tests for TorchInstaller     #
####################################


def test_torch_installer_install_high() -> None:
    installer = TorchInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.3.1")
        run_mock.assert_called_once_with("pip install -U torch==2.3.1")


def test_torch_installer_install_low() -> None:
    installer = TorchInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2.1.1")
        run_mock.assert_called_once_with("pip install -U torch==2.1.1 numpy==1.26.4")


#####################################
#     Tests for XarrayInstaller     #
#####################################


def test_xarray_installer_install_high() -> None:
    installer = XarrayInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2024.6")
        run_mock.assert_called_once_with("pip install -U xarray==2024.6")


def test_xarray_installer_install_low() -> None:
    installer = XarrayInstaller()
    with patch("feu.install.run_bash_command") as run_mock:
        installer.install("2023.8")
        run_mock.assert_called_once_with("pip install -U xarray==2023.8 numpy==1.26.4")


######################################
#     Tests for PackageInstaller     #
######################################


def test_package_installer_install_numpy() -> None:
    with patch("feu.install.run_bash_command") as run_mock:
        PackageInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


def test_package_installer_install_pandas() -> None:
    with patch("feu.install.run_bash_command") as run_mock:
        PackageInstaller.install(package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("pip install -U pandas==2.1.1 numpy==1.26.4")


#####################################
#     Tests for install_package     #
#####################################


def test_install_package_numpy() -> None:
    with patch("feu.install.run_bash_command") as run_mock:
        install_package(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


def test_install_package_pandas() -> None:
    with patch("feu.install.run_bash_command") as run_mock:
        install_package(package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("pip install -U pandas==2.1.1 numpy==1.26.4")
