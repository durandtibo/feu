from __future__ import annotations

from unittest.mock import patch

from feu.installer.pip import (
    DependencyResolver,
    PackageInstaller,
    PipCommandGenerator,
)

######################################
#     Tests for PackageInstaller     #
######################################


def test_package_installer_repr() -> None:
    assert repr(
        PackageInstaller(resolver=DependencyResolver("numpy"), command=PipCommandGenerator())
    ).startswith("PackageInstaller(")


def test_package_installer_str() -> None:
    assert str(
        PackageInstaller(resolver=DependencyResolver("numpy"), command=PipCommandGenerator())
    ).startswith("PackageInstaller(")


def test_pip_package_installer_install() -> None:
    installer = PackageInstaller(
        resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    )
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        installer.install("2.0.0")
        run_mock.assert_called_once_with("pip install numpy==2.0.0")


def test_package_installer_generate_multiple_packages() -> None:
    assert (
        PipCommandGenerator().generate(["numpy==2.0.0", "pandas>=2.0,<3.0"])
        == "pip install numpy==2.0.0 pandas>=2.0,<3.0"
    )


def test_package_installer_install_with_args() -> None:
    installer = PackageInstaller(
        resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    )
    with patch("feu.installer.pip.package.run_bash_command") as run_mock:
        installer.install("2.0.0", args="-U")
        run_mock.assert_called_once_with("pip install -U numpy==2.0.0")
