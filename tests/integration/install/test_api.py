from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

from feu import is_package_available
from feu.compat import Target, UnsupportedVersionError, find_closest_version
from feu.imports import clear_availability_caches
from feu.install import (
    InstallerSpec,
    PipInstaller,
    UvInstaller,
    install_package,
    install_package_closest_version,
)
from feu.testing import pip_available, requests_available, uv_available
from feu.utils.package import PackageSpec
from feu.utils.platform import get_python_version


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    clear_availability_caches()


@pytest.fixture(scope="module")
def pkg_name() -> str:
    return "cowsay"


@pytest.fixture(scope="module")
def pkg_version(pkg_name: str) -> str:
    return find_closest_version(
        pkg_name=pkg_name,
        pkg_version="6.1",
        target=Target(python_version=get_python_version()),
    )


#####################################
#     Tests for install_package     #
#####################################


@pip_available
def test_install_package_pip(pkg_name: str, pkg_version: str) -> None:
    """Test that a package is installed with pip."""
    install_package(
        installer=InstallerSpec("pip"), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


@uv_available
def test_install_package_uv(pkg_name: str, pkg_version: str) -> None:
    """Test that a package is installed with uv."""
    install_package(
        installer=InstallerSpec("uv"), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


#####################################################
#     Tests for install_package_closest_version     #
#####################################################


@pip_available
def test_install_package_closest_version_pip(pkg_name: str, pkg_version: str) -> None:
    """Test that the closest version of a package is installed with
    pip."""
    install_package_closest_version(
        installer=InstallerSpec("pip"), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


@uv_available
def test_install_package_closest_version_uv(pkg_name: str, pkg_version: str) -> None:
    """Test that the closest version of a package is installed with
    uv."""
    install_package_closest_version(
        installer=InstallerSpec("uv"), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


@pip_available
@requests_available
def test_install_package_closest_version_open_wildcard_is_installed_as_requested() -> None:
    """Test that an open wildcard is resolved with the real PyPI data
    and installed as requested."""
    with patch("feu.install.installer.run_command") as run_mock:
        install_package_closest_version(
            installer=InstallerSpec("pip"),
            package=PackageSpec(name="numpy", version="2.*"),
            target=Target(python_version="3.14"),
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==2.*"])


@pip_available
@requests_available
def test_install_package_closest_version_closed_wildcard_is_resolved() -> None:
    """Test that a closed wildcard is resolved to the latest compatible
    version with the real PyPI data."""
    with patch("feu.install.installer.run_command") as run_mock:
        install_package_closest_version(
            installer=InstallerSpec("pip"),
            package=PackageSpec(name="numpy", version="1.*"),
            target=Target(python_version="3.9"),
        )
        run_mock.assert_called_once_with([sys.executable, "-m", "pip", "install", "numpy==1.26.4"])


@requests_available
def test_install_package_closest_version_wildcard_without_match_raises_before_install() -> None:
    """Test that a wildcard without match raises before any install with
    the real PyPI data."""
    with (
        patch("feu.install.installer.run_command") as run_mock,
        pytest.raises(UnsupportedVersionError, match=r"matches '1\.24\.\*'"),
    ):
        install_package_closest_version(
            installer=InstallerSpec("pip"),
            package=PackageSpec(name="numpy", version="1.24.*"),
            target=Target(python_version="3.14"),
        )
    run_mock.assert_not_called()


#################################
#     Tests for the installers  #
#################################


@pip_available
def test_pip_installer(pkg_name: str, pkg_version: str) -> None:
    """Test that the pip installer installs a package."""
    PipInstaller().install(PackageSpec(name=pkg_name, version=pkg_version))
    assert is_package_available(pkg_name)


@uv_available
def test_uv_installer(pkg_name: str, pkg_version: str) -> None:
    """Test that the uv installer installs a package."""
    UvInstaller().install(PackageSpec(name=pkg_name, version=pkg_version))
    assert is_package_available(pkg_name)
