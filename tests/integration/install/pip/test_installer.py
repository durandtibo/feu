from __future__ import annotations

import pytest

from feu import is_package_available
from feu.compat import Target, find_closest_version
from feu.install.pip import PipInstaller, UvInstaller
from feu.testing import pip_available, uv_available
from feu.utils.package import PackageSpec
from feu.version import get_python_major_minor


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    is_package_available.cache_clear()


@pytest.fixture(scope="module")
def package() -> PackageSpec:
    return PackageSpec(
        name="cowsay",
        version=find_closest_version(
            pkg_name="cowsay",
            pkg_version="6.1",
            target=Target(python_version=get_python_major_minor()),
        ),
    )


@pip_available
def test_pip_installer(package: PackageSpec) -> None:
    PipInstaller().install(package)


@uv_available
def test_uv_installer(package: PackageSpec) -> None:
    UvInstaller().install(package)
    assert is_package_available(package.name)
