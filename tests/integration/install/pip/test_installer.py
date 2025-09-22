from __future__ import annotations

from sys import version_info

import pytest

from feu import is_package_available
from feu.installer.pip import PipInstaller, PipxInstaller, UvInstaller
from feu.package import find_closest_version
from feu.testing import pip_available, pipx_available, uv_available


@pytest.fixture(scope="module")
def python_version() -> str:
    return f"{version_info.major}.{version_info.minor}"


@pytest.fixture(scope="module")
def numpy_version(python_version: str) -> str:
    return find_closest_version(
        pkg_name="numpy", pkg_version="2.2.5", python_version=python_version
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
