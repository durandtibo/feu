from __future__ import annotations

import pytest
from packaging.version import Version

from feu.compat.registry import UNSUPPORTED, CompatRegistry, UnsupportedVersionError
from feu.compat.target import Target

T311 = Target(python_version="3.11")
T310 = Target(python_version="3.10")
T315 = Target(python_version="3.15")

##################################
#     Tests for CompatRegistry    #
##################################


def test_compat_registry_init_empty() -> None:
    registry = CompatRegistry()
    assert registry.base == {}
    assert registry.overrides == {}


def test_compat_registry_init_with_state() -> None:
    registry = CompatRegistry({"numpy": {T311: {"min": "1.0.0", "max": None}}})
    assert registry.base == {"numpy": {T311: {"min": "1.0.0", "max": None}}}
    assert registry.overrides == {}


def test_compat_registry_init_copies_state() -> None:
    state = {"numpy": {T311: {"min": "1.0.0", "max": None}}}
    registry = CompatRegistry(state)
    registry.register("torch", T311, pkg_version_min="2.0.0", pkg_version_max=None, layer="base")
    assert "torch" not in state


def test_compat_registry_repr() -> None:
    registry = CompatRegistry()
    assert repr(registry).startswith("CompatRegistry(")


def test_compat_registry_str() -> None:
    registry = CompatRegistry()
    assert str(registry).startswith("CompatRegistry(")


def test_compat_registry_register_default_layer_is_override() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.0.2")
    assert registry.overrides == {"my_package": {T311: {"min": "1.2.0", "max": "2.0.2"}}}
    assert registry.base == {}


def test_compat_registry_register_base_layer() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.0.2", layer="base")
    assert registry.base == {"my_package": {T311: {"min": "1.2.0", "max": "2.0.2"}}}
    assert registry.overrides == {}


def test_compat_registry_register_multiple() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.0.2", layer="base")
    registry.register("my_package", T310, pkg_version_min="1.1.0", pkg_version_max="1.5.2", layer="base")
    assert registry.base == {
        "my_package": {
            T311: {"min": "1.2.0", "max": "2.0.2"},
            T310: {"min": "1.1.0", "max": "1.5.2"},
        }
    }


def test_compat_registry_register_exist_ok_false_same_layer() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.1.0", pkg_version_max="1.5.2", layer="base")
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.0.2", layer="base")


def test_compat_registry_register_override_never_conflicts_with_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.1.0", pkg_version_max="1.5.2", layer="base")
    # No exist_ok needed: override layer is independent of base layer.
    registry.register("my_package", T311, pkg_version_min="9.0.0", pkg_version_max=None)
    assert registry.overrides == {"my_package": {T311: {"min": "9.0.0", "max": None}}}
    assert registry.base == {"my_package": {T311: {"min": "1.1.0", "max": "1.5.2"}}}


def test_compat_registry_register_exist_ok_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.1.0", pkg_version_max="1.5.2", layer="base")
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.0.2", layer="base", exist_ok=True)
    assert registry.base == {"my_package": {T311: {"min": "1.2.0", "max": "2.0.2"}}}


def test_compat_registry_register_many() -> None:
    registry = CompatRegistry()
    registry.register_many(
        {
            "numpy": {T311: {"min": "1.23.2", "max": "2.4.6"}},
            "torch": {T311: {"min": "2.0.0", "max": None}},
        },
        layer="base",
    )
    assert registry.base == {
        "numpy": {T311: {"min": "1.23.2", "max": "2.4.6"}},
        "torch": {T311: {"min": "2.0.0", "max": None}},
    }


def test_compat_registry_register_many_exist_ok_false() -> None:
    registry = CompatRegistry()
    registry.register_many({"numpy": {T311: {"min": "1.0.0", "max": None}}}, layer="base")
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register_many({"numpy": {T311: {"min": "2.0.0", "max": None}}}, layer="base")


def test_compat_registry_register_many_exist_ok_true() -> None:
    registry = CompatRegistry()
    registry.register_many({"numpy": {T311: {"min": "1.0.0", "max": None}}}, layer="base")
    registry.register_many(
        {"numpy": {T311: {"min": "2.0.0", "max": None}}}, layer="base", exist_ok=True
    )
    assert registry.base == {"numpy": {T311: {"min": "2.0.0", "max": None}}}


def test_compat_registry_get_config_override_wins_over_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.0.0", pkg_version_max=None, layer="base")
    registry.register("my_package", T311, pkg_version_min="2.0.0", pkg_version_max=None, layer="override")
    assert registry.get_config(pkg_name="my_package", target=T311) == {
        "min": "2.0.0",
        "max": None,
    }


def test_compat_registry_get_config_falls_back_to_base() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.0.0", pkg_version_max=None, layer="base")
    assert registry.get_config(pkg_name="my_package", target=T311) == {
        "min": "1.0.0",
        "max": None,
    }


def test_compat_registry_get_config_empty_registry() -> None:
    registry = CompatRegistry()
    assert registry.get_config(pkg_name="my_package", target=T311) == {}


def test_compat_registry_get_config_no_matching_target() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T310, pkg_version_min="1.0.0", pkg_version_max=None, layer="base")
    assert registry.get_config(pkg_name="my_package", target=T311) == {}


#############################################
#     Tests for wildcard/specificity match   #
#############################################


def test_compat_registry_os_wildcard_matches_any_os() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.0.0", pkg_version_max=None, layer="base")
    linux_target = Target(python_version="3.11", os="linux")
    assert registry.get_config(pkg_name="my_package", target=linux_target) == {
        "min": "1.0.0",
        "max": None,
    }


def test_compat_registry_more_specific_entry_wins() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.0.0", pkg_version_max=None, layer="base")
    registry.register(
        "my_package",
        Target(python_version="3.11", os="macos", arch="arm64"),
        pkg_version_min="5.0.0",
        pkg_version_max=None,
        layer="base",
    )
    macos_arm = Target(python_version="3.11", os="macos", arch="arm64")
    linux = Target(python_version="3.11", os="linux")
    assert registry.get_config(pkg_name="my_package", target=macos_arm) == {
        "min": "5.0.0",
        "max": None,
    }
    assert registry.get_config(pkg_name="my_package", target=linux) == {
        "min": "1.0.0",
        "max": None,
    }


def test_compat_registry_free_threaded_must_match_exactly() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package", Target(python_version="3.14", free_threaded=True), pkg_version_min="1.0.0", pkg_version_max=None,
        layer="base",
    )
    non_free_threaded = Target(python_version="3.14", free_threaded=False)
    assert registry.get_config(pkg_name="my_package", target=non_free_threaded) == {}


def test_compat_registry_most_recent_wins_among_ties() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package", Target(python_version="3.11", os="linux"), pkg_version_min="1.0.0", pkg_version_max=None, layer="base"
    )
    registry.register(
        "my_package", Target(python_version="3.11", arch="x86_64"), pkg_version_min="2.0.0", pkg_version_max=None, layer="base"
    )
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    # Both entries match with equal specificity (one non-None field each);
    # the most recently registered one wins.
    assert registry.get_config(pkg_name="my_package", target=target) == {
        "min": "2.0.0",
        "max": None,
    }


########################################
#     Tests for min/max/closest/valid  #
########################################


def test_compat_registry_get_min_and_max_versions() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.2.0", layer="base")
    assert registry.get_min_and_max_versions(pkg_name="my_package", target=T311) == (
        Version("1.2.0"),
        Version("2.2.0"),
    )


def test_compat_registry_get_min_and_max_versions_empty() -> None:
    registry = CompatRegistry()
    assert registry.get_min_and_max_versions(pkg_name="my_package", target=T311) == (None, None)


def test_compat_registry_find_closest_version_valid() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.2.0", layer="base")
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_missing() -> None:
    registry = CompatRegistry()
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)
        == "2.0.0"
    )


def test_compat_registry_find_closest_version_lower() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.2.0", layer="base")
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="1.0.0", target=T311)
        == "1.2.0"
    )


def test_compat_registry_find_closest_version_higher() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.2.0", layer="base")
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="3.0.0", target=T311)
        == "2.2.0"
    )


def test_compat_registry_is_valid_version_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.2.0", layer="base")
    assert registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)


def test_compat_registry_is_valid_version_false_min() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.2.0", layer="base")
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="1.0.0", target=T311)


def test_compat_registry_is_valid_version_false_max() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.2.0", layer="base")
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="3.0.0", target=T311)


def test_compat_registry_is_valid_version_empty() -> None:
    registry = CompatRegistry()
    assert registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)


###################################
#     Tests for UNSUPPORTED       #
###################################


def test_compat_registry_is_unsupported_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, pkg_version_min=UNSUPPORTED, pkg_version_max=UNSUPPORTED, layer="base")
    assert registry.is_unsupported(pkg_name="my_package", target=T315)


def test_compat_registry_is_unsupported_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, pkg_version_min="1.2.0", pkg_version_max="2.2.0", layer="base")
    assert not registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_is_unsupported_unconfigured() -> None:
    registry = CompatRegistry()
    assert not registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_get_min_and_max_versions_unsupported_raises() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, pkg_version_min=UNSUPPORTED, pkg_version_max=UNSUPPORTED, layer="base")
    with pytest.raises(UnsupportedVersionError, match=r"No version of package my_package"):
        registry.get_min_and_max_versions(pkg_name="my_package", target=T315)


def test_compat_registry_find_closest_version_unsupported_raises() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, pkg_version_min=UNSUPPORTED, pkg_version_max=UNSUPPORTED, layer="base")
    with pytest.raises(UnsupportedVersionError, match=r"No version of package my_package"):
        registry.find_closest_version(pkg_name="my_package", pkg_version="2.0.0", target=T315)


def test_compat_registry_is_valid_version_unsupported_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, pkg_version_min=UNSUPPORTED, pkg_version_max=UNSUPPORTED, layer="base")
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T315)
