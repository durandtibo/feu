from __future__ import annotations

from unittest.mock import patch

from feu.installer.pip.command import (
    PipCommandGenerator,
    PipxCommandGenerator,
    UvCommandGenerator,
)
from feu.installer.pip.package import PackageInstaller, create_package_installer_mapping
from feu.installer.pip.resolver import (
    DependencyResolver,
    JaxDependencyResolver,
    TorchDependencyResolver,
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


def test_package_installer_equal_true() -> None:
    assert PackageInstaller(
        resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    ).equal(PackageInstaller(resolver=DependencyResolver("numpy"), command=PipCommandGenerator()))


def test_package_installer_equal_false_different_resolver() -> None:
    assert not PackageInstaller(
        resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    ).equal(PackageInstaller(resolver=DependencyResolver("torch"), command=PipCommandGenerator()))


def test_package_installer_equal_false_different_command() -> None:
    assert not PackageInstaller(
        resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    ).equal(PackageInstaller(resolver=DependencyResolver("numpy"), command=UvCommandGenerator()))


def test_package_installer_equal_false_different_type() -> None:
    assert not PackageInstaller(
        resolver=DependencyResolver("numpy"), command=PipCommandGenerator()
    ).equal(42)


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


######################################################
#     Tests for create_package_installer_mapping     #
######################################################


def test_create_package_installer_mapping_packages() -> None:
    assert set(create_package_installer_mapping(command=PipCommandGenerator())) == {
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


def test_create_package_installer_mapping_pipx() -> None:
    assert create_package_installer_mapping(command=PipxCommandGenerator())["torch"].equal(
        PackageInstaller(resolver=TorchDependencyResolver(), command=PipxCommandGenerator())
    )


def test_create_package_installer_mapping_uv() -> None:
    assert create_package_installer_mapping(command=UvCommandGenerator())["torch"].equal(
        PackageInstaller(resolver=TorchDependencyResolver(), command=UvCommandGenerator())
    )


def test_create_package_installer_mapping_jax() -> None:
    assert create_package_installer_mapping(command=PipCommandGenerator())["jax"].equal(
        PackageInstaller(resolver=JaxDependencyResolver(), command=PipCommandGenerator())
    )


def test_create_package_installer_mapping_torch() -> None:
    assert create_package_installer_mapping(command=PipCommandGenerator())["torch"].equal(
        PackageInstaller(resolver=TorchDependencyResolver(), command=PipCommandGenerator())
    )
