from __future__ import annotations

from unittest.mock import patch

from feu.install.pip.installer2 import (
    PipInstaller,
    PipxInstaller,
)
from feu.utils.package import PackageSpec

##################################
#     Tests for PipInstaller     #
##################################


def test_pip_installer_repr() -> None:
    assert repr(PipInstaller()).startswith("PipInstaller(")


def test_pip_installer_str() -> None:
    assert str(PipInstaller()).startswith("PipInstaller(")


def test_pip_installer_install_numpy() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        PipInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_pip_installer_install_pandas() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        PipInstaller().install(PackageSpec(name="pandas", version="2.1.1"))
        run_mock.assert_called_once_with("pip install pandas==2.1.1 numpy<2.0.0")


def test_pip_installer_install_numpy_with_args() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        PipInstaller(arguments="-U").install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


###################################
#     Tests for PipxInstaller     #
###################################


def test_pipx_installer_repr() -> None:
    assert repr(PipxInstaller()).startswith("PipxInstaller(")


def test_pipx_installer_str() -> None:
    assert str(PipxInstaller()).startswith("PipxInstaller(")


def test_pipx_installer_install_numpy() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        PipxInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with("pipx install numpy==2.0.0")


def test_pipx_installer_install_pandas() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        PipxInstaller().install(PackageSpec(name="pandas", version="2.1.1"))
        run_mock.assert_called_once_with("pipx install pandas==2.1.1 numpy<2.0.0")


def test_pipx_installer_install_numpy_with_args() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        PipxInstaller(arguments="-U").install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with("pipx install -U numpy==2.0.0")
