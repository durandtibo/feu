from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from feu.install.pip import (
    PipInstaller,
    PipxInstaller,
    UvInstaller,
)
from feu.install.pip.package import BasePackageInstaller

PACKAGE_NAMES = {
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
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        PipInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_pip_installer_install_pandas() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        PipInstaller.install(package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("pip install pandas==2.1.1 numpy<2.0.0")


def test_pip_installer_install_numpy_with_args() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
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
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        PipInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_pip_installer_registry() -> None:
    assert set(PipInstaller.registry) == PACKAGE_NAMES


###################################
#     Tests for PipxInstaller     #
###################################


@patch.dict(PipxInstaller.registry, {}, clear=True)
def test_pipx_installer_add_installer() -> None:
    installer = Mock(spec=BasePackageInstaller)
    PipxInstaller.add_installer("pandas", installer)
    assert PipxInstaller.registry["pandas"] == installer


@patch.dict(PipxInstaller.registry, {}, clear=True)
def test_pipx_installer_add_installer_duplicate_exist_ok_true() -> None:
    installer = Mock(spec=BasePackageInstaller)
    PipxInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    PipxInstaller.add_installer("pandas", installer, exist_ok=True)
    assert PipxInstaller.registry["pandas"] == installer


@patch.dict(PipxInstaller.registry, {}, clear=True)
def test_pipx_installer_add_installer_duplicate_exist_ok_false() -> None:
    installer = Mock(spec=BasePackageInstaller)
    PipxInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    with pytest.raises(RuntimeError, match=r"An installer (.*) is already registered"):
        PipxInstaller.add_installer("pandas", installer)


@patch.dict(PipxInstaller.registry, {}, clear=True)
def test_pipx_installer_has_installer_false() -> None:
    assert not PipxInstaller.has_installer("pandas")


@patch.dict(PipxInstaller.registry, {}, clear=True)
def test_pipx_installer_has_installer_true() -> None:
    PipxInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    assert PipxInstaller.has_installer("pandas")


def test_pipx_installer_install_numpy() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        PipxInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pipx install numpy==2.0.0")


def test_pipx_installer_install_pandas() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        PipxInstaller.install(package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("pipx install pandas==2.1.1 numpy<2.0.0")


def test_pipx_installer_install_numpy_with_args() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        PipxInstaller.install(package="numpy", version="2.0.0", args="-U")
        run_mock.assert_called_once_with("pipx install -U numpy==2.0.0")


@patch.dict(PipxInstaller.registry, {}, clear=True)
def test_pipx_installer_install_mock() -> None:
    installer = Mock(spec=BasePackageInstaller)
    PipxInstaller.add_installer("numpy", installer)
    PipxInstaller.install(package="numpy", version="2.0.0", args="-U")
    installer.install.assert_called_once_with(version="2.0.0", args="-U")


@patch.dict(PipxInstaller.registry, {}, clear=True)
def test_pipx_installer_install_default() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        PipxInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pipx install numpy==2.0.0")


def test_pipx_installer_registry() -> None:
    assert set(PipxInstaller.registry) == PACKAGE_NAMES


#################################
#     Tests for UvInstaller     #
#################################


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_add_installer() -> None:
    installer = Mock(spec=BasePackageInstaller)
    UvInstaller.add_installer("pandas", installer)
    assert UvInstaller.registry["pandas"] == installer


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_add_installer_duplicate_exist_ok_true() -> None:
    installer = Mock(spec=BasePackageInstaller)
    UvInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    UvInstaller.add_installer("pandas", installer, exist_ok=True)
    assert UvInstaller.registry["pandas"] == installer


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_add_installer_duplicate_exist_ok_false() -> None:
    installer = Mock(spec=BasePackageInstaller)
    UvInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    with pytest.raises(RuntimeError, match=r"An installer (.*) is already registered"):
        UvInstaller.add_installer("pandas", installer)


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_add_installer_with_optional_dependencies() -> None:
    installer1 = Mock(spec=BasePackageInstaller)
    installer2 = Mock(spec=BasePackageInstaller)
    UvInstaller.add_installer("requests", installer1)
    UvInstaller.add_installer("requests[security]", installer2)
    assert UvInstaller.registry["requests"] == installer1
    assert UvInstaller.registry["requests[security]"] == installer2


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_has_installer_false() -> None:
    assert not UvInstaller.has_installer("pandas")


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_has_installer_true() -> None:
    UvInstaller.add_installer("pandas", Mock(spec=BasePackageInstaller))
    assert UvInstaller.has_installer("pandas")


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_has_installer_true_optional_dependencies_explicit() -> None:
    UvInstaller.add_installer("requests", Mock(spec=BasePackageInstaller))
    UvInstaller.add_installer("requests[security]", Mock(spec=BasePackageInstaller))
    assert UvInstaller.has_installer("requests[security]")


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_has_installer_true_optional_dependencies_implicit() -> None:
    UvInstaller.add_installer("requests", Mock(spec=BasePackageInstaller))
    assert UvInstaller.has_installer("requests[security]")


def test_uv_installer_install_numpy() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        UvInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_uv_installer_install_pandas() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        UvInstaller.install(package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("uv pip install pandas==2.1.1 numpy<2.0.0")


def test_uv_installer_install_numpy_with_args() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        UvInstaller.install(package="numpy", version="2.0.0", args="-U")
        run_mock.assert_called_once_with("uv pip install -U numpy==2.0.0")


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_install_mock() -> None:
    installer = Mock(spec=BasePackageInstaller)
    UvInstaller.add_installer("numpy", installer)
    UvInstaller.install(package="numpy", version="2.0.0", args="-U")
    installer.install.assert_called_once_with(version="2.0.0", args="-U")


@patch.dict(UvInstaller.registry, {}, clear=True)
def test_uv_installer_install_default() -> None:
    with patch("feu.install.pip.package.run_bash_command") as run_mock:
        UvInstaller.install(package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_uv_installer_registry() -> None:
    assert set(UvInstaller.registry) == PACKAGE_NAMES
