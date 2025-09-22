from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.installer.pip import BasePackageInstaller, PipInstaller

##################################
#     Tests for PipInstaller     #
##################################


@patch.dict(PipInstaller.registry, {}, clear=True)
def test_pip_installer_add_installer() -> None:
    installer = Mock(spec=BasePackageInstaller)
    PipInstaller.add_installer("pandas", installer)
    assert PipInstaller.registry["pandas"] == installer


@patch.dict(PipInstaller.registry, {}, clear=True)
def test_pip_installer_add_installer_duplicate_exist_ok_true() -> None:
    installer = Mock(spec=BasePackageInstaller)
    PipInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    PipInstaller.add_installer("pandas", installer, exist_ok=True)
    assert PipInstaller.registry["pandas"] == installer


@patch.dict(PipInstaller.registry, {}, clear=True)
def test_pip_installer_add_installer_duplicate_exist_ok_false() -> None:
    installer = Mock(spec=BasePackageInstaller)
    PipInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    with pytest.raises(RuntimeError, match=r"An installer (.*) is already registered"):
        PipInstaller.add_installer("pandas", installer)


@patch.dict(PipInstaller.registry, {}, clear=True)
def test_pip_installer_has_installer_false() -> None:
    assert not PipInstaller.has_installer("pandas")


@patch.dict(PipInstaller.registry, {}, clear=True)
def test_pip_installer_has_installer_true() -> None:
    PipInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    assert PipInstaller.has_installer("pandas")


def test_pip_installer_install_numpy() -> None:
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        PipInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_pip_installer_install_pandas() -> None:
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        PipInstaller.install(package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("pip install pandas==2.1.1 numpy<2.0.0")


def test_pip_installer_install_numpy_with_args() -> None:
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        PipInstaller.install(package="numpy", version="2.0.0", args="-U")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


@patch.dict(PipInstaller.registry, {}, clear=True)
def test_pip_installer_install_mock() -> None:
    installer = Mock(spec=BasePackageInstaller)
    PipInstaller.add_installer("numpy", installer)
    PipInstaller.install(package="numpy", version="2.0.0", args="-U")
    installer.install.assert_called_once_with(version="2.0.0", args="-U")


@patch.dict(PipInstaller.registry, {}, clear=True)
def test_pip_installer_install_default() -> None:
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        PipInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_pip_installer_registry() -> None:
    assert set(PipInstaller.registry) == {
        "jax",
        "matplotlib",
        "pandas",
        "pyarrow",
        "scikit-learn",
        "scipy",
        "sklearn",
        "torch",
        "xarray",
    }
