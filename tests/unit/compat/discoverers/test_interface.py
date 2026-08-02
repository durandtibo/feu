from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from feu.compat.discoverers import (
    BaseCompatDiscoverer,
    CompatDiscovererRegistry,
    discover_compat_targets,
    get_default_registry,
    register_discoverers,
)
from feu.compat.registry import VersionRange
from feu.compat.target import Target

if TYPE_CHECKING:
    from collections.abc import Generator

MODULE = "feu.compat.discoverers.default"


@pytest.fixture(autouse=True)
def _reset_default_registry() -> Generator[None, None, None]:
    """Reset the registry before and after each test."""
    if hasattr(get_default_registry, "_registry"):
        del get_default_registry._registry
    yield
    if hasattr(get_default_registry, "_registry"):
        del get_default_registry._registry


class StubCompatDiscoverer(BaseCompatDiscoverer):
    def discover(self, pkg_name, targets) -> dict:  # noqa: ANN001, ARG002
        return {target: [VersionRange("42.0.0", None)] for target in targets}


##############################################
#     Tests for discover_compat_targets      #
##############################################


@patch(
    f"{MODULE}.fetch_pypi_wheel_filenames",
    lambda *_args: {"1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",)},
)
def test_discover_compat_targets_uses_default_discoverer() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    compat = discover_compat_targets("pkg", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("1.0.0", None)]}


def test_discover_compat_targets_uses_registered_discoverer() -> None:
    linux_311 = Target(python_version="3.11", os="linux", arch="x86_64")
    register_discoverers({"stub_pkg": StubCompatDiscoverer()})
    compat = discover_compat_targets("stub_pkg", targets=(linux_311,))
    assert compat == {linux_311: [VersionRange("42.0.0", None)]}


##########################################
#     Tests for register_discoverers     #
##########################################


def test_register_discoverers_calls_registry() -> None:
    register_discoverers({"stub_pkg": StubCompatDiscoverer()})
    assert get_default_registry().has_discoverer("stub_pkg")


def test_register_discoverers_with_exist_ok_true() -> None:
    register_discoverers({"stub_pkg": StubCompatDiscoverer()})
    register_discoverers({"stub_pkg": StubCompatDiscoverer()}, exist_ok=True)


def test_register_discoverers_with_exist_ok_false() -> None:
    register_discoverers({"stub_pkg": StubCompatDiscoverer()})
    with pytest.raises(RuntimeError, match=r"already registered"):
        register_discoverers({"stub_pkg": StubCompatDiscoverer()}, exist_ok=False)


##########################################
#     Tests for get_default_registry     #
##########################################


def test_get_default_registry_returns_registry() -> None:
    assert isinstance(get_default_registry(), CompatDiscovererRegistry)


def test_get_default_registry_returns_singleton() -> None:
    assert get_default_registry() is get_default_registry()


def test_get_default_registry_singleton_persists_modifications() -> None:
    registry1 = get_default_registry()
    assert not registry1.has_discoverer("stub_pkg")
    registry1.register("stub_pkg", StubCompatDiscoverer())

    registry2 = get_default_registry()
    assert registry1 is registry2
    assert registry2.has_discoverer("stub_pkg")
