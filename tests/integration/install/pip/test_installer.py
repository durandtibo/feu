from __future__ import annotations

import pytest

from feu import is_package_available
from feu.install.pip import PipInstaller, PipxInstaller, UvInstaller
from feu.package import find_closest_version
from feu.testing import pip_available, pipx_available, uv_available
from feu.utils.package import PackageSpec
from feu.versio import get_python_major_minor


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture(scope="module")
def package() -> PackageSpec:
    return PackageSpec(
        name="mkdocs",
        version=find_closest_version(
            pkg_name="mkdocs", pkg_version="1.6.1", python_version=get_python_major_minor()
        ),
    )


@pip_available
def test_pip_installer(package: PackageSpec) -> None:
    PipInstaller().install(package)
    assert is_package_available(package.name)


@pipx_available
def test_pipx_installer(package: PackageSpec) -> None:
    PipxInstaller().install(package)
    assert is_package_available(package.name)


@uv_available
def test_uv_installer(package: PackageSpec) -> None:
    UvInstaller().install(package)
    assert is_package_available(package.name)
