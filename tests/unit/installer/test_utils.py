from unittest.mock import patch

import pytest

from feu.installer import (
    get_available_installers,
    install_package,
    is_pip_available,
    is_pipx_available,
    is_uv_available,
)
from feu.testing import pip_available, pipx_available, uv_available


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
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        install_package(installer="pip", package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_install_package_pip_pandas() -> None:
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        install_package(installer="pip", package="pandas", version="2.1.1")
        run_mock.assert_called_once_with("pip install pandas==2.1.1 numpy<2.0.0")


def test_install_package_uv_numpy() -> None:
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        install_package(installer="uv", package="numpy", version="2.0.0")
        run_mock.assert_called_once_with("uv pip install numpy==2.0.0")


def test_install_package_pip_numpy_with_args() -> None:
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        install_package(installer="pip", package="numpy", version="2.0.0", args="-U")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")


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


@patch("feu.installer.utils.is_pip_available", lambda: True)
def test_get_available_installers_pip_available() -> None:
    assert "pip" in get_available_installers()


@patch("feu.installer.utils.is_pip_available", lambda: False)
def test_get_available_installers_pip_not_available() -> None:
    assert "pip" not in get_available_installers()


@pip_available
def test_get_available_installers_pip() -> None:
    assert "pip" in get_available_installers()


@patch("feu.installer.utils.is_pipx_available", lambda: True)
def test_get_available_installers_pipx_available() -> None:
    assert "pipx" in get_available_installers()


@patch("feu.installer.utils.is_pipx_available", lambda: False)
def test_get_available_installers_pipx_not_available() -> None:
    assert "pipx" not in get_available_installers()


@pipx_available
def test_get_available_installers_pipx() -> None:
    assert "pipx" in get_available_installers()


@patch("feu.installer.utils.is_uv_available", lambda: True)
def test_get_available_installers_uv_available() -> None:
    assert "uv" in get_available_installers()


@patch("feu.installer.utils.is_uv_available", lambda: False)
def test_get_available_installers_uv_not_available() -> None:
    assert "uv" not in get_available_installers()


@uv_available
def test_get_available_installers_uv() -> None:
    assert "uv" in get_available_installers()
