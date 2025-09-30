from __future__ import annotations

from unittest.mock import patch

from feu.install.pip.installer2 import (
    PipInstaller,
    PipxInstaller,
    UvInstaller,
)
from feu.utils.package import PackageSpec

##################################
#     Tests for PipInstaller     #
##################################


def test_pip_installer_repr() -> None:
    assert repr(PipInstaller()).startswith("PipInstaller(")


def test_pip_installer_str() -> None:
    assert str(PipInstaller()).startswith("PipInstaller(")


def test_pip_installer_equal_true() -> None:
    assert PipInstaller().equal(PipInstaller())


def test_pip_installer_equal_true_with_args() -> None:
    assert PipInstaller("-U").equal(PipInstaller("-U"))


def test_pip_installer_equal_false_different_args() -> None:
    assert not PipInstaller("-U").equal(PipInstaller("-F"))


def test_pip_installer_equal_false_different_type() -> None:
    assert not PipInstaller("-U").equal(42)


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


def test_pipx_installer_equal_true() -> None:
    assert PipxInstaller().equal(PipxInstaller())


def test_pipx_installer_equal_true_with_args() -> None:
    assert PipxInstaller("-U").equal(PipxInstaller("-U"))


def test_pipx_installer_equal_false_different_args() -> None:
    assert not PipxInstaller("-U").equal(PipxInstaller("-F"))


def test_pipx_installer_equal_false_different_type() -> None:
    assert not PipxInstaller("-U").equal(42)


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


#################################
#     Tests for UvInstaller     #
#################################


def test_uv_installer_repr() -> None:
    assert repr(UvInstaller()).startswith("UvInstaller(")


def test_uv_installer_str() -> None:
    assert str(UvInstaller()).startswith("UvInstaller(")


def test_uv_installer_equal_true() -> None:
    assert UvInstaller().equal(UvInstaller())


def test_uv_installer_equal_true_with_args() -> None:
    assert UvInstaller("-U").equal(UvInstaller("-U"))


def test_uv_installer_equal_false_different_args() -> None:
    assert not UvInstaller("-U").equal(UvInstaller("-F"))


def test_uv_installer_equal_false_different_type() -> None:
    assert not UvInstaller("-U").equal(42)


def test_uv_installer_install_numpy() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        UvInstaller().install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_uv_installer_install_pandas() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        UvInstaller().install(PackageSpec(name="pandas", version="2.1.1"))
        run_mock.assert_called_once_with("uv pip install pandas==2.1.1 numpy<2.0.0")


def test_uv_installer_install_numpy_with_args() -> None:
    with patch("feu.install.pip.installer2.run_bash_command") as run_mock:
        UvInstaller(arguments="-U").install(PackageSpec(name="numpy", version="2.0.0"))
        run_mock.assert_called_once_with("uv pip install -U numpy==2.0.0")
