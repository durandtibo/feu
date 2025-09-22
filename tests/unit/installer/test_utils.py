from unittest.mock import patch

from feu.installer import install_package

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
