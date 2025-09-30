from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.install import InstallerRegistry
from feu.install.pip.installer2 import PipInstaller, PipxInstaller
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec

#######################################
#     Tests for InstallerRegistry     #
#######################################


@patch.dict(InstallerRegistry.registry, {}, clear=True)
def test_installer_registry_add_installer() -> None:
    InstallerRegistry.add_installer("pip", PipInstaller)
    assert InstallerRegistry.registry["pip"] == PipInstaller


@patch.dict(InstallerRegistry.registry, {}, clear=True)
def test_installer_registry_add_installer_duplicate_exist_ok_true() -> None:
    InstallerRegistry.add_installer("pip", PipxInstaller)
    InstallerRegistry.add_installer("pip", PipInstaller, exist_ok=True)
    assert InstallerRegistry.registry["pip"] == PipInstaller


@patch.dict(InstallerRegistry.registry, {}, clear=True)
def test_installer_registry_add_installer_duplicate_exist_ok_false() -> None:
    InstallerRegistry.add_installer("pip", PipInstaller)
    with pytest.raises(RuntimeError, match=r"An installer (.*) is already registered"):
        InstallerRegistry.add_installer("pip", PipInstaller)


@patch.dict(InstallerRegistry.registry, {}, clear=True)
def test_installer_registry_has_installer_false() -> None:
    assert not InstallerRegistry.has_installer("pip")


@patch.dict(InstallerRegistry.registry, {}, clear=True)
def test_installer_registry_has_installer_true() -> None:
    InstallerRegistry.add_installer("pip", PipInstaller)
    assert InstallerRegistry.has_installer("pip")


def test_installer_registry_install_pip_numpy() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        InstallerRegistry.install(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_installer_registry_install_pip_pandas() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        InstallerRegistry.install(
            installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.1.1")
        )
        run_mock.assert_called_once_with("pip install pandas==2.1.1 numpy<2.0.0")


def test_installer_registry_install_uv_numpy() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        InstallerRegistry.install(
            installer=InstallerSpec("uv"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_installer_registry_install_pip_numpy_with_args() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        InstallerRegistry.install(
            installer=InstallerSpec(name="pip", arguments="-U"),
            package=PackageSpec(name="numpy", version="2.0.0"),
        )
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


def test_installer_registry_registry() -> None:
    assert set(InstallerRegistry.registry) == {"pip", "pipx", "uv"}
