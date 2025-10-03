from __future__ import annotations

import pytest

from feu import is_package_available
from feu.install import (
    get_available_installers,
    install_package,
    install_package_closest_version,
)
from feu.package import find_closest_version
from feu.utils.installer import InstallerSpec
from feu.utils.package import PackageSpec
from feu.version import get_python_major_minor


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture(scope="module")
def pkg_name() -> str:
    return "mkdocs"


@pytest.fixture(scope="module")
def pkg_version(pkg_name: str) -> str:
    return find_closest_version(
        pkg_name=pkg_name, pkg_version="1.6.1", python_version=get_python_major_minor()
    )


#####################################
#     Tests for install_package     #
#####################################


@pytest.mark.parametrize("installer", get_available_installers())
def test_install_package(installer: str, pkg_name: str, pkg_version: str) -> None:
    install_package(
        installer=InstallerSpec(installer), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)


#####################################################
#     Tests for install_package_closest_version     #
#####################################################


@pytest.mark.parametrize("installer", get_available_installers())
def test_install_package_closest_version(installer: str, pkg_name: str, pkg_version: str) -> None:
    install_package_closest_version(
        installer=InstallerSpec(installer), package=PackageSpec(name=pkg_name, version=pkg_version)
    )
    assert is_package_available(pkg_name)
