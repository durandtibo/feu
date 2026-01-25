from __future__ import annotations

from feu.install.installer import BaseInstaller
from feu.utils.package import PackageSpec


class MockInstaller(BaseInstaller):
    """A mock installer for testing BaseInstaller abstract methods."""

    def __init__(self, arguments: str = "") -> None:
        self._arguments = arguments
        self.install_called = False
        self.last_package = None

    def equal(self, other: object) -> bool:
        if not isinstance(other, MockInstaller):
            return False
        return self._arguments == other._arguments

    def install(self, package: PackageSpec) -> None:
        self.install_called = True
        self.last_package = package

    @classmethod
    def instantiate_with_arguments(cls, arguments: str) -> MockInstaller:
        return cls(arguments=arguments)


####################################
#     Tests for BaseInstaller      #
####################################


def test_base_installer_equal_same() -> None:
    installer1 = MockInstaller(arguments="--upgrade")
    installer2 = MockInstaller(arguments="--upgrade")
    assert installer1.equal(installer2)


def test_base_installer_equal_different_args() -> None:
    installer1 = MockInstaller(arguments="--upgrade")
    installer2 = MockInstaller(arguments="--force")
    assert not installer1.equal(installer2)


def test_base_installer_equal_different_type() -> None:
    installer1 = MockInstaller(arguments="--upgrade")
    assert not installer1.equal("not an installer")


def test_base_installer_install() -> None:
    installer = MockInstaller()
    package = PackageSpec(name="numpy", version="2.0.0")
    installer.install(package)
    assert installer.install_called
    assert installer.last_package == package


def test_base_installer_instantiate_with_arguments() -> None:
    installer = MockInstaller.instantiate_with_arguments(arguments="--verbose")
    expected = MockInstaller(arguments="--verbose")
    assert installer.equal(expected)


def test_base_installer_instantiate_with_arguments_equal() -> None:
    installer1 = MockInstaller.instantiate_with_arguments(arguments="--verbose")
    installer2 = MockInstaller(arguments="--verbose")
    assert installer1.equal(installer2)
