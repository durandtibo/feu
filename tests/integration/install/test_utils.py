from __future__ import annotations

import pytest

from feu import is_package_available
from feu.install import (
    get_available_installers,
    install_package,
    install_package_closest_version,
)
from feu.package import find_closest_version
from feu.utils.version import get_python_major_minor


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture(scope="module")
def numpy_version() -> str:
    return find_closest_version(
        pkg_name="numpy", pkg_version="2.2.5", python_version=get_python_major_minor()
    )


#####################################
#     Tests for install_package     #
#####################################


@pytest.mark.parametrize("installer", get_available_installers())
def test_install_package(installer: str, numpy_version: str) -> None:
    install_package(installer=installer, package="numpy", version=numpy_version)
    assert is_package_available("numpy")


#####################################################
#     Tests for install_package_closest_version     #
#####################################################


@pytest.mark.parametrize("installer", get_available_installers())
def test_install_package_closest_version(installer: str) -> None:
    install_package_closest_version(installer=installer, package="numpy", version="2.2.5")
    assert is_package_available("numpy")
