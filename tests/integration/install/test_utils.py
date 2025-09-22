from __future__ import annotations

from sys import version_info

import pytest

from feu import is_package_available
from feu.installer import get_available_installers, install_package
from feu.package import find_closest_version

PACKAGES = [("numpy", "2.2.5")]


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture
def python_version() -> str:
    return f"{version_info.major}.{version_info.minor}"


#####################################
#     Tests for install_package     #
#####################################


@pytest.mark.parametrize("installer", get_available_installers())
@pytest.mark.parametrize(("package", "version"), PACKAGES)
def test_install_package(installer: str, package: str, version: str, python_version: str) -> None:
    version = find_closest_version(
        pkg_name=package, pkg_version=version, python_version=python_version
    )
    install_package(installer=installer, package=package, version=version)
    assert is_package_available(package)
