from __future__ import annotations

import pytest
from packaging.version import Version

from feu.compat.registry import CompatRegistry

##################################
#     Tests for CompatRegistry     #
##################################


def test_compat_registry_init_empty() -> None:
    registry = CompatRegistry()
    assert registry.registry == {}


def test_compat_registry_init_with_state() -> None:
    registry = CompatRegistry({"numpy": {"3.11": {"min": "1.0.0", "max": None}}})
    assert registry.registry == {"numpy": {"3.11": {"min": "1.0.0", "max": None}}}


def test_compat_registry_init_copies_state() -> None:
    state = {"numpy": {"3.11": {"min": "1.0.0", "max": None}}}
    registry = CompatRegistry(state)
    registry.register("torch", "3.11", "2.0.0", None)
    assert "torch" not in state


def test_compat_registry_repr() -> None:
    registry = CompatRegistry()
    assert repr(registry).startswith("CompatRegistry(")


def test_compat_registry_str() -> None:
    registry = CompatRegistry()
    assert str(registry).startswith("CompatRegistry(")


def test_compat_registry_register() -> None:
    registry = CompatRegistry()
    registry.register(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
    )
    assert registry.registry == {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}}


def test_compat_registry_register_multiple() -> None:
    registry = CompatRegistry()
    registry.register(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
    )
    registry.register(
        pkg_name="my_package",
        python_version="3.10",
        pkg_version_min="1.1.0",
        pkg_version_max="1.5.2",
    )
    assert registry.registry == {
        "my_package": {
            "3.10": {"min": "1.1.0", "max": "1.5.2"},
            "3.11": {"min": "1.2.0", "max": "2.0.2"},
        }
    }


def test_compat_registry_register_exist_ok_false() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.1.0", "max": "1.5.2"}}})
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register(
            pkg_name="my_package",
            python_version="3.11",
            pkg_version_min="1.2.0",
            pkg_version_max="2.0.2",
        )


def test_compat_registry_register_exist_ok_true() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.1.0", "max": "1.5.2"}}})
    registry.register(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
        exist_ok=True,
    )
    assert registry.registry == {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}}


def test_compat_registry_register_many() -> None:
    registry = CompatRegistry()
    registry.register_many(
        {
            "numpy": {"3.11": {"min": "1.23.2", "max": "2.4.6"}},
            "torch": {"3.11": {"min": "2.0.0", "max": None}},
        }
    )
    assert registry.registry == {
        "numpy": {"3.11": {"min": "1.23.2", "max": "2.4.6"}},
        "torch": {"3.11": {"min": "2.0.0", "max": None}},
    }


def test_compat_registry_register_many_exist_ok_false() -> None:
    registry = CompatRegistry({"numpy": {"3.11": {"min": "1.0.0", "max": None}}})
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register_many({"numpy": {"3.11": {"min": "2.0.0", "max": None}}})


def test_compat_registry_register_many_exist_ok_true() -> None:
    registry = CompatRegistry({"numpy": {"3.11": {"min": "1.0.0", "max": None}}})
    registry.register_many(
        {"numpy": {"3.11": {"min": "2.0.0", "max": None}}}, exist_ok=True
    )
    assert registry.registry == {"numpy": {"3.11": {"min": "2.0.0", "max": None}}}


def test_compat_registry_get_config() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}})
    assert registry.get_config(pkg_name="my_package", python_version="3.11") == {
        "min": "1.2.0",
        "max": "2.0.2",
    }


def test_compat_registry_get_config_empty_registry() -> None:
    registry = CompatRegistry()
    assert registry.get_config(pkg_name="my_package", python_version="3.11") == {}


def test_compat_registry_get_config_empty_pkg_name() -> None:
    registry = CompatRegistry({"my_package": {}})
    assert registry.get_config(pkg_name="my_package", python_version="3.11") == {}


def test_compat_registry_get_config_empty_python_version() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {}}})
    assert registry.get_config(pkg_name="my_package", python_version="3.11") == {}


def test_compat_registry_get_min_and_max_versions() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert registry.get_min_and_max_versions(pkg_name="my_package", python_version="3.11") == (
        Version("1.2.0"),
        Version("2.2.0"),
    )


def test_compat_registry_get_min_and_max_versions_min_only() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": None}}})
    assert registry.get_min_and_max_versions(pkg_name="my_package", python_version="3.11") == (
        Version("1.2.0"),
        None,
    )


def test_compat_registry_get_min_and_max_versions_max_only() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": None, "max": "2.2.0"}}})
    assert registry.get_min_and_max_versions(pkg_name="my_package", python_version="3.11") == (
        None,
        Version("2.2.0"),
    )


def test_compat_registry_get_min_and_max_versions_empty() -> None:
    registry = CompatRegistry()
    assert registry.get_min_and_max_versions(pkg_name="my_package", python_version="3.11") == (
        None,
        None,
    )


def test_compat_registry_find_closest_version_valid() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
        )
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_missing() -> None:
    registry = CompatRegistry()
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
        )
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_lower() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="1.0.0", python_version="3.11"
        )
        == "1.2.0"
    )


def test_compat_registry_find_closest_version_higher() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert (
        registry.find_closest_version(
            pkg_name="my_package", pkg_version="3.0.0", python_version="3.11"
        )
        == "2.2.0"
    )


def test_compat_registry_is_valid_version_true() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert registry.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


def test_compat_registry_is_valid_version_false_min() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert not registry.is_valid_version(
        pkg_name="my_package", pkg_version="1.0.0", python_version="3.11"
    )


def test_compat_registry_is_valid_version_false_max() -> None:
    registry = CompatRegistry({"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}})
    assert not registry.is_valid_version(
        pkg_name="my_package", pkg_version="3.0.0", python_version="3.11"
    )


def test_compat_registry_is_valid_version_empty() -> None:
    registry = CompatRegistry()
    assert registry.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )
