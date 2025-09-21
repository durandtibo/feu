from __future__ import annotations

from unittest.mock import patch

from feu.installer.pip import PipPackageInstaller

#########################################
#     Tests for PipPackageInstaller     #
#########################################


def test_pip_package_installer_repr() -> None:
    assert repr(PipPackageInstaller()).startswith("PipPackageInstaller(")


def test_pip_package_installer_str() -> None:
    assert str(PipPackageInstaller()).startswith("PipPackageInstaller(")


def test_default_installer_install() -> None:
    installer = PipPackageInstaller()
    with patch("feu.installer.pip.installer.run_bash_command") as run_mock:
        installer.install(["numpy==2.0.0"])
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_default_installer_install_multiple_packages() -> None:
    installer = PipPackageInstaller()
    with patch("feu.installer.pip.installer.run_bash_command") as run_mock:
        installer.install(["numpy==2.0.0", "pandas>=2.0,<3.0"])
        run_mock.assert_called_once_with("pip install numpy==2.0.0 pandas>=2.0,<3.0")


def test_default_installer_install_with_args() -> None:
    installer = PipPackageInstaller()
    with patch("feu.installer.pip.installer.run_bash_command") as run_mock:
        installer.install(["numpy==2.0.0"], args="-U")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")
