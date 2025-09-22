from unittest.mock import patch

from feu.installer import install_package, is_pip_available, is_pipx_available
from feu.testing import pip_available, pipx_available

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
