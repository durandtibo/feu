from __future__ import annotations

from sys import version_info

import pytest

from feu import is_package_available
from feu.install import get_available_installers, install_package
from feu.package import find_closest_version


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture(scope="module")
def python_version() -> str:
    return f"{version_info.major}.{version_info.minor}"


@pytest.fixture(scope="module")
def numpy_version(python_version: str) -> str:
    return find_closest_version(
        pkg_name="numpy", pkg_version="2.2.5", python_version=python_version
    )


#####################################
#     Tests for install_package     #
#####################################


@pytest.mark.parametrize("installer", get_available_installers())
def test_install_package(installer: str, numpy_version: str) -> None:
    install_package(installer=installer, package="numpy", version=numpy_version)
    assert is_package_available("numpy")
