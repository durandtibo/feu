from __future__ import annotations

import pytest

from feu import is_package_available
from feu.install.pip import PipInstaller, PipxInstaller, UvInstaller
from feu.package import find_closest_version
from feu.testing import pip_available, pipx_available, uv_available
from feu.utils.version import get_python_major_minor


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture(scope="module")
def numpy_version() -> str:
    return find_closest_version(
        pkg_name="numpy", pkg_version="2.2.5", python_version=get_python_major_minor()
    )


@pip_available
def test_pip_installer(numpy_version: str) -> None:
    PipInstaller().install(package="numpy", version=numpy_version)
    assert is_package_available("numpy")


@pipx_available
def test_pipx_installer(numpy_version: str) -> None:
    PipxInstaller().install(package="numpy", version=numpy_version)
    assert is_package_available("numpy")


@uv_available
def test_uv_installer(numpy_version: str) -> None:
    UvInstaller().install(package="numpy", version=numpy_version)
    assert is_package_available("numpy")
