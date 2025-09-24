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
def pkg_name() -> str:
    return "mkdocs"


@pytest.fixture(scope="module")
def pkg_version(pkg_name: str) -> str:
    return find_closest_version(
        pkg_name=pkg_name, pkg_version="1.6.1", python_version=get_python_major_minor()
    )


@pip_available
def test_pip_installer(pkg_name: str, pkg_version: str) -> None:
    PipInstaller().install(package=pkg_name, version=pkg_version)
    assert is_package_available(pkg_name)


@pipx_available
def test_pipx_installer(pkg_name: str, pkg_version: str) -> None:
    PipxInstaller().install(package="mkdocs", version=pkg_version)
    assert is_package_available(pkg_name)


@uv_available
def test_uv_installer(pkg_name: str, pkg_version: str) -> None:
    UvInstaller().install(package=pkg_name, version=pkg_version)
    assert is_package_available(pkg_name)
