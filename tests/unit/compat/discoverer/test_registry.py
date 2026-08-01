from __future__ import annotations

import pytest

from feu.compat.discoverer import (
    BaseCompatDiscoverer,
    CompatDiscoverer,
    CompatDiscovererRegistry,
)


class StubCompatDiscoverer(BaseCompatDiscoverer):
    def discover(self, pkg_name, targets) -> dict:  # noqa: ANN001, ARG002
        return {}


##############################################
#     Tests for CompatDiscovererRegistry     #
##############################################


def test_compat_discoverer_registry_init_empty() -> None:
    registry = CompatDiscovererRegistry()
    assert len(registry._state) == 0


def test_compat_discoverer_registry_init_with_state() -> None:
    discoverer = StubCompatDiscoverer()
    initial_state = {"my_package": discoverer}
    registry = CompatDiscovererRegistry(initial_state)

    assert registry._state["my_package"] is discoverer
    # Verify it's a copy
    initial_state["other_package"] = StubCompatDiscoverer()
    assert "other_package" not in registry._state


def test_compat_discoverer_registry_repr() -> None:
    assert repr(CompatDiscovererRegistry()).startswith("CompatDiscovererRegistry(")


def test_compat_discoverer_registry_has_discoverer_false_by_default() -> None:
    registry = CompatDiscovererRegistry()
    assert not registry.has_discoverer("unregistered_pkg")


def test_compat_discoverer_registry_find_discoverer_default() -> None:
    registry = CompatDiscovererRegistry()
    discoverer = registry.find_discoverer("unregistered_pkg")
    assert isinstance(discoverer, CompatDiscoverer)


def test_compat_discoverer_registry_register_new_package() -> None:
    registry = CompatDiscovererRegistry()
    discoverer = StubCompatDiscoverer()
    registry.register("my_package", discoverer)
    assert registry.has_discoverer("my_package")
    assert registry.find_discoverer("my_package") is discoverer


def test_compat_discoverer_registry_register_existing_package_without_exist_ok() -> None:
    registry = CompatDiscovererRegistry()
    registry.register("my_package", StubCompatDiscoverer())
    with pytest.raises(RuntimeError, match=r"already registered"):
        registry.register("my_package", StubCompatDiscoverer(), exist_ok=False)


def test_compat_discoverer_registry_register_existing_package_with_exist_ok() -> None:
    registry = CompatDiscovererRegistry()
    registry.register("my_package", StubCompatDiscoverer())
    discoverer = StubCompatDiscoverer()
    registry.register("my_package", discoverer, exist_ok=True)
    assert registry.find_discoverer("my_package") is discoverer


def test_compat_discoverer_registry_register_many() -> None:
    registry = CompatDiscovererRegistry()
    registry.register_many(
        {
            "package1": StubCompatDiscoverer(),
            "package2": StubCompatDiscoverer(),
        }
    )
    assert registry.has_discoverer("package1")
    assert registry.has_discoverer("package2")


def test_compat_discoverer_registry_register_many_with_existing_package() -> None:
    registry = CompatDiscovererRegistry({"package1": StubCompatDiscoverer()})
    with pytest.raises(RuntimeError, match=r"already registered"):
        registry.register_many(
            {"package1": StubCompatDiscoverer(), "package2": StubCompatDiscoverer()}
        )
