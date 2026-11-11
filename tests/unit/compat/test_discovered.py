from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

import pytest
from packaging.version import Version

from feu.compat.discovered import register_discovered
from feu.compat.packages import get_package_names
from feu.compat.registry import CompatRegistry
from feu.compat.target import Target

if TYPE_CHECKING:
    from types import ModuleType

PACKAGES = get_package_names()


def _module(pkg_name: str) -> ModuleType:
    return importlib.import_module(f"feu.compat.discovered.{pkg_name.replace('-', '_').lower()}")


def _bounds(pkg_name: str) -> set[str]:
    return {
        bound
        for ranges in _module(pkg_name).compat().values()
        for version_range in ranges
        for bound in (version_range.min, version_range.max)
        if bound is not None
    }


#####################################
#     Tests for register_discovered #
#####################################


def test_register_discovered_registers_versions() -> None:
    registry = CompatRegistry()
    register_discovered(registry)
    assert registry.get_compatible_versions("numpy", Target(python_version="3.9"), "1.26.*") == [
        "1.26.0",
        "1.26.1",
        "1.26.2",
        "1.26.3",
        "1.26.4",
    ]


def test_register_discovered_registers_every_package() -> None:
    registry = CompatRegistry()
    register_discovered(registry)
    assert set(registry.state) == {name.lower() for name in PACKAGES}


#######################################
#     Data contract of the VERSIONS   #
#######################################


@pytest.mark.parametrize("pkg_name", PACKAGES)
def test_versions_are_sorted_in_pep440_order(pkg_name: str) -> None:
    versions = _module(pkg_name).VERSIONS
    assert list(versions) == sorted(versions, key=Version)


@pytest.mark.parametrize("pkg_name", PACKAGES)
def test_versions_are_unique(pkg_name: str) -> None:
    versions = _module(pkg_name).VERSIONS
    assert len(set(versions)) == len(versions)


@pytest.mark.parametrize("pkg_name", PACKAGES)
def test_versions_are_stable(pkg_name: str) -> None:
    versions = _module(pkg_name).VERSIONS
    assert not [v for v in versions if Version(v).is_prerelease or Version(v).is_postrelease]


@pytest.mark.parametrize("pkg_name", PACKAGES)
def test_versions_are_not_empty(pkg_name: str) -> None:
    assert len(_module(pkg_name).VERSIONS) > 0


@pytest.mark.parametrize("pkg_name", PACKAGES)
def test_range_bounds_are_in_versions(pkg_name: str) -> None:
    assert _bounds(pkg_name) <= set(_module(pkg_name).VERSIONS)
