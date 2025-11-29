from unittest.mock import Mock, patch

import pytest

from feu.install import (
    get_available_installers,
    install_package,
    install_package_closest_version,
    is_pip_available,
    is_pipx_available,
    is_uv_available,
)
from feu.testing import pip_available, pipx_available, uv_available
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec


@pytest.fixture(autouse=True)
def _reset() -> None:
    is_pip_available.cache_clear()
    is_pipx_available.cache_clear()
    is_uv_available.cache_clear()
    get_available_installers.cache_clear()


#####################################
#     Tests for install_package     #
#####################################


def test_install_package_pip_numpy() -> None:
    with patch("feu.install.pip.installer.run_bash_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("python -m pip install numpy==2.0.0")


def test_install_package_pip_pandas() -> None:
    with patch("feu.install.pip.installer.run_bash_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.1.1")
        )
        run_mock.assert_called_once_with("python -m pip install pandas==2.1.1 numpy<2.0.0")


def test_install_package_uv_numpy() -> None:
    with patch("feu.install.pip.installer.run_bash_command") as run_mock:
        install_package(
            installer=InstallerSpec("uv"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_install_package_pip_numpy_with_args() -> None:
    with patch("feu.install.pip.installer.run_bash_command") as run_mock:
        install_package(
            installer=InstallerSpec("pip", arguments="-U"),
            package=PackageSpec(name="numpy", version="2.0.0"),
        )
        run_mock.assert_called_once_with("python -m pip install -U numpy==2.0.0")


#####################################################
#     Tests for install_package_closest_version     #
#####################################################


def test_install_package_closest_version_pip_numpy() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("python -m pip install numpy==2.0.0")


def test_install_package_closest_version_pip_pandas() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"), package=PackageSpec(name="pandas", version="2.1.1")
        )
        run_mock.assert_called_once_with("python -m pip install pandas==2.1.1 numpy<2.0.0")


def test_install_package_closest_version_uv_numpy() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("uv"), package=PackageSpec(name="numpy", version="2.0.0")
        )
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_install_package_closest_version_pip_numpy_with_args() -> None:
    with (
        patch("feu.install.utils.get_python_major_minor", Mock(return_value="3.12")),
        patch("feu.install.pip.installer.run_bash_command") as run_mock,
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip", arguments="-U"),
            package=PackageSpec(name="numpy", version="2.0.0"),
        )
        run_mock.assert_called_once_with("python -m pip install -U numpy==2.0.0")


######################################
#     Tests for is_pip_available     #
######################################


def test_is_pip_available() -> None:
    assert isinstance(is_pip_available(), bool)


@pip_available
def test_is_pip_available_true() -> None:
    assert is_pip_available()


#######################################
#     Tests for is_pipx_available     #
#######################################


def test_is_pipx_available() -> None:
    assert isinstance(is_pipx_available(), bool)


@pipx_available
def test_is_pipx_available_true() -> None:
    assert is_pipx_available()


#####################################
#     Tests for is_uv_available     #
#####################################


def test_is_uv_available() -> None:
    assert isinstance(is_uv_available(), bool)


@uv_available
def test_is_uv_available_true() -> None:
    assert is_uv_available()


##############################################
#     Tests for get_available_installers     #
##############################################


@patch("feu.install.utils.is_pip_available", lambda: True)
def test_get_available_installers_pip_available() -> None:
    assert "pip" in get_available_installers()


@patch("feu.install.utils.is_pip_available", lambda: False)
def test_get_available_installers_pip_not_available() -> None:
    assert "pip" not in get_available_installers()


@pip_available
def test_get_available_installers_pip() -> None:
    assert "pip" in get_available_installers()


@patch("feu.install.utils.is_pipx_available", lambda: True)
def test_get_available_installers_pipx_available() -> None:
    assert "pipx" in get_available_installers()


@patch("feu.install.utils.is_pipx_available", lambda: False)
def test_get_available_installers_pipx_not_available() -> None:
    assert "pipx" not in get_available_installers()


@pipx_available
def test_get_available_installers_pipx() -> None:
    assert "pipx" in get_available_installers()


@patch("feu.install.utils.is_uv_available", lambda: True)
def test_get_available_installers_uv_available() -> None:
    assert "uv" in get_available_installers()


@patch("feu.install.utils.is_uv_available", lambda: False)
def test_get_available_installers_uv_not_available() -> None:
    assert "uv" not in get_available_installers()


@uv_available
def test_get_available_installers_uv() -> None:
    assert "uv" in get_available_installers()
