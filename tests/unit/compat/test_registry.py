from __future__ import annotations

import pytest
from packaging.version import InvalidVersion, Version

from feu.compat.registry import CompatRegistry, UnsupportedVersionError, VersionRange, _parse
from feu.compat.target import Target

T311 = Target(python_version="3.11")
T310 = Target(python_version="3.10")
T315 = Target(python_version="3.15")

##################################
#     Tests for CompatRegistry    #
##################################


def test_compat_registry_init_empty() -> None:
    registry = CompatRegistry()
    assert registry.state == {}


def test_compat_registry_init_with_state() -> None:
    registry = CompatRegistry({"numpy": {T311: [VersionRange("1.0.0", None)]}})
    assert registry.state == {"numpy": {T311: [VersionRange("1.0.0", None)]}}


def test_compat_registry_init_copies_state() -> None:
    state = {"numpy": {T311: [VersionRange("1.0.0", None)]}}
    registry = CompatRegistry(state)
    registry.register("torch", T311, ranges=[VersionRange("2.0.0", None)])
    assert "torch" not in state


def test_compat_registry_repr() -> None:
    registry = CompatRegistry()
    assert repr(registry).startswith("CompatRegistry(")


def test_compat_registry_str() -> None:
    registry = CompatRegistry()
    assert str(registry).startswith("CompatRegistry(")


def test_compat_registry_register() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.0.2")])
    assert registry.state == {"my-package": {T311: [VersionRange("1.2.0", "2.0.2")]}}


def test_compat_registry_register_multiple_ranges() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
    )
    assert registry.state == {
        "pydantic": {T311: [VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)]}
    }


def test_compat_registry_register_multiple_targets() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.0.2")])
    registry.register("my_package", T310, ranges=[VersionRange("1.1.0", "1.5.2")])
    assert registry.state == {
        "my-package": {
            T311: [VersionRange("1.2.0", "2.0.2")],
            T310: [VersionRange("1.1.0", "1.5.2")],
        }
    }


def test_compat_registry_register_exist_ok_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.1.0", "1.5.2")])
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.0.2")])


def test_compat_registry_register_exist_ok_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.1.0", "1.5.2")])
    registry.register(
        "my_package",
        T311,
        ranges=[VersionRange("1.2.0", "2.0.2")],
        exist_ok=True,
    )
    assert registry.state == {"my-package": {T311: [VersionRange("1.2.0", "2.0.2")]}}


def test_compat_registry_register_many() -> None:
    registry = CompatRegistry()
    registry.register_many(
        {
            "numpy": {T311: [VersionRange("1.23.2", "2.4.6")]},
            "torch": {T311: [VersionRange("2.0.0", None)]},
        },
    )
    assert registry.state == {
        "numpy": {T311: [VersionRange("1.23.2", "2.4.6")]},
        "torch": {T311: [VersionRange("2.0.0", None)]},
    }


def test_compat_registry_register_many_exist_ok_false() -> None:
    registry = CompatRegistry()
    registry.register_many({"numpy": {T311: [VersionRange("1.0.0", None)]}})
    with pytest.raises(
        RuntimeError, match=r"A package configuration .* is already registered for package"
    ):
        registry.register_many({"numpy": {T311: [VersionRange("2.0.0", None)]}})


def test_compat_registry_register_many_exist_ok_true() -> None:
    registry = CompatRegistry()
    registry.register_many({"numpy": {T311: [VersionRange("1.0.0", None)]}})
    registry.register_many({"numpy": {T311: [VersionRange("2.0.0", None)]}}, exist_ok=True)
    assert registry.state == {"numpy": {T311: [VersionRange("2.0.0", None)]}}


def test_compat_registry_get_config() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.0.0", None)])
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("1.0.0", None)]


def test_compat_registry_get_config_empty_registry() -> None:
    registry = CompatRegistry()
    assert registry.get_config(pkg_name="my_package", target=T311) == []


def test_compat_registry_get_config_no_matching_target() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T310, ranges=[VersionRange("1.0.0", None)])
    assert registry.get_config(pkg_name="my_package", target=T311) == []


#############################################
#     Tests for wildcard/specificity match   #
#############################################


def test_compat_registry_os_wildcard_matches_any_os() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.0.0", None)])
    linux_target = Target(python_version="3.11", os="linux")
    assert registry.get_config(pkg_name="my_package", target=linux_target) == [
        VersionRange("1.0.0", None)
    ]


def test_compat_registry_more_specific_entry_wins() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.0.0", None)])
    registry.register(
        "my_package",
        Target(python_version="3.11", os="macos", arch="arm64"),
        ranges=[VersionRange("5.0.0", None)],
    )
    macos_arm = Target(python_version="3.11", os="macos", arch="arm64")
    linux = Target(python_version="3.11", os="linux")
    assert registry.get_config(pkg_name="my_package", target=macos_arm) == [
        VersionRange("5.0.0", None)
    ]
    assert registry.get_config(pkg_name="my_package", target=linux) == [VersionRange("1.0.0", None)]


def test_compat_registry_free_threaded_must_match_exactly() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package",
        Target(python_version="3.14", free_threaded=True),
        ranges=[VersionRange("1.0.0", None)],
    )
    non_free_threaded = Target(python_version="3.14", free_threaded=False)
    assert registry.get_config(pkg_name="my_package", target=non_free_threaded) == []


def test_compat_registry_equal_specificity_entries_are_merged() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package",
        Target(python_version="3.11", os="linux"),
        ranges=[VersionRange("1.0.0", "1.5.0")],
    )
    registry.register(
        "my_package",
        Target(python_version="3.11", arch="x86_64"),
        ranges=[VersionRange("2.0.0", None)],
    )
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    assert registry.get_config(pkg_name="my_package", target=target) == [
        VersionRange("1.0.0", "1.5.0"),
        VersionRange("2.0.0", None),
    ]


def test_compat_registry_lower_specificity_entry_does_not_override_best() -> None:
    registry = CompatRegistry()
    registry.register(
        "my_package",
        Target(python_version="3.11", os="macos", arch="arm64"),
        ranges=[VersionRange("5.0.0", None)],
    )
    registry.register(
        "my_package",
        Target(python_version="3.11", os="macos"),
        ranges=[VersionRange("1.0.0", None)],
    )
    target = Target(python_version="3.11", os="macos", arch="arm64")
    # The second, less specific entry is registered after the first, more
    # specific one, but must not override it as the best match.
    assert registry.get_config(pkg_name="my_package", target=target) == [
        VersionRange("5.0.0", None)
    ]


########################################
#     Tests for ranges/closest/valid   #
########################################


def test_compat_registry_get_version_ranges() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")])
    assert registry.get_version_ranges(pkg_name="my_package", target=T311) == [
        (Version("1.2.0"), Version("2.2.0"))
    ]


def test_compat_registry_get_version_ranges_multiple() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange(None, "1.10.13"), VersionRange("2.0.0", None)],
    )
    assert registry.get_version_ranges(pkg_name="pydantic", target=T311) == [
        (None, Version("1.10.13")),
        (Version("2.0.0"), None),
    ]


def test_compat_registry_get_version_ranges_empty() -> None:
    registry = CompatRegistry()
    assert registry.get_version_ranges(pkg_name="my_package", target=T311) == []


def test_compat_registry_find_closest_version_valid() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")])
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
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")])
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="1.0.0", target=T311)
        == "1.2.0"
    )


def test_compat_registry_find_closest_version_higher() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")])
    assert (
        registry.find_closest_version(pkg_name="my_package", pkg_version="3.0.0", target=T311)
        == "2.2.0"
    )


def test_compat_registry_find_closest_version_in_first_range() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.0.0", None)],
    )
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="1.5.0", target=T311)
        == "1.5.0"
    )


def test_compat_registry_find_closest_version_gap_snaps_up() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.8.0", None)],
    )
    # 2.0.0 falls between the two ranges: snap up to the next range's min.
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="2.0.0", target=T311)
        == "2.8.0"
    )


def test_compat_registry_find_closest_version_gap_snaps_up_unordered_registration() -> None:
    registry = CompatRegistry()
    # Ranges registered out of ascending order must still be treated as sorted.
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("2.8.0", None), VersionRange("1.0.0", "1.10.13")],
    )
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="2.0.0", target=T311)
        == "2.8.0"
    )


def test_compat_registry_find_closest_version_below_all_ranges() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.8.0", None)],
    )
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="0.5.0", target=T311)
        == "1.0.0"
    )


def test_compat_registry_find_closest_version_above_all_ranges() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.0.0", "2.5.0")],
    )
    assert (
        registry.find_closest_version(pkg_name="pydantic", pkg_version="9.0.0", target=T311)
        == "2.5.0"
    )


def test_compat_registry_find_closest_version_empty() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[])
    with pytest.raises(
        UnsupportedVersionError, match="No version of package my_package is compatible with target"
    ):
        registry.find_closest_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)


def test_compat_registry_is_valid_version_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")])
    assert registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)


def test_compat_registry_is_valid_version_false_min() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")])
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="1.0.0", target=T311)


def test_compat_registry_is_valid_version_false_max() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")])
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="3.0.0", target=T311)


def test_compat_registry_is_valid_version_empty() -> None:
    registry = CompatRegistry()
    assert registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T311)


def test_compat_registry_is_valid_version_second_range() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.8.0", None)],
    )
    assert registry.is_valid_version(pkg_name="pydantic", pkg_version="3.0.0", target=T311)


def test_compat_registry_is_valid_version_in_gap_false() -> None:
    registry = CompatRegistry()
    registry.register(
        "pydantic",
        T311,
        ranges=[VersionRange("1.0.0", "1.10.13"), VersionRange("2.8.0", None)],
    )
    assert not registry.is_valid_version(pkg_name="pydantic", pkg_version="2.0.0", target=T311)


###################################
#     Tests for unsupported       #
###################################


def test_compat_registry_is_unsupported_true() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, ranges=[])
    assert registry.is_unsupported(pkg_name="my_package", target=T315)


def test_compat_registry_is_unsupported_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.2.0", "2.2.0")])
    assert not registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_is_unsupported_unconfigured() -> None:
    registry = CompatRegistry()
    assert not registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_get_version_ranges_unsupported_raises() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, ranges=[])
    with pytest.raises(UnsupportedVersionError, match=r"No version of package my_package"):
        registry.get_version_ranges(pkg_name="my_package", target=T315)


def test_compat_registry_find_closest_version_unsupported_raises() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, ranges=[])
    with pytest.raises(UnsupportedVersionError, match=r"No version of package my_package"):
        registry.find_closest_version(pkg_name="my_package", pkg_version="2.0.0", target=T315)


def test_compat_registry_is_valid_version_unsupported_false() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T315, ranges=[])
    assert not registry.is_valid_version(pkg_name="my_package", pkg_version="2.0.0", target=T315)


#########################################
#     Tests for unspecified platform    #
#########################################

LINUX_X86 = Target(python_version="3.11", os="linux", arch="x86_64")
MACOS_ARM = Target(python_version="3.11", os="macos", arch="arm64")
WINDOWS_X86 = Target(python_version="3.11", os="windows", arch="x86_64")


@pytest.fixture
def platform_registry() -> CompatRegistry:
    registry = CompatRegistry()
    registry.register("my_package", LINUX_X86, ranges=[VersionRange("1.0.0", "2.0.0")])
    registry.register("my_package", MACOS_ARM, ranges=[VersionRange("1.5.0", "3.0.0")])
    registry.register("my_package", WINDOWS_X86, ranges=[VersionRange("5.0.0", "6.0.0")])
    return registry


def test_compat_registry_unspecified_platform_returns_union(
    platform_registry: CompatRegistry,
) -> None:
    assert platform_registry.get_config(pkg_name="my_package", target=T311) == [
        VersionRange("1.0.0", "3.0.0"),
        VersionRange("5.0.0", "6.0.0"),
    ]


def test_compat_registry_unspecified_arch_matches_the_os() -> None:
    registry = CompatRegistry()
    registry.register("my_package", LINUX_X86, ranges=[VersionRange("1.0.0", "2.0.0")])
    registry.register("my_package", MACOS_ARM, ranges=[VersionRange("3.0.0", "4.0.0")])
    target = Target(python_version="3.11", os="macos")
    assert registry.get_config(pkg_name="my_package", target=target) == [
        VersionRange("3.0.0", "4.0.0")
    ]


def test_compat_registry_unspecified_os_matches_the_arch() -> None:
    registry = CompatRegistry()
    registry.register("my_package", LINUX_X86, ranges=[VersionRange("1.0.0", "2.0.0")])
    registry.register("my_package", MACOS_ARM, ranges=[VersionRange("3.0.0", "4.0.0")])
    target = Target(python_version="3.11", arch="arm64")
    assert registry.get_config(pkg_name="my_package", target=target) == [
        VersionRange("3.0.0", "4.0.0")
    ]


def test_compat_registry_fully_specified_target_uses_its_entry(
    platform_registry: CompatRegistry,
) -> None:
    assert platform_registry.get_config(pkg_name="my_package", target=MACOS_ARM) == [
        VersionRange("1.5.0", "3.0.0")
    ]


def test_compat_registry_wildcard_entry_loses_to_concrete_entry_for_unspecified_lookup() -> None:
    registry = CompatRegistry()
    registry.register("my_package", T311, ranges=[VersionRange("1.0.0", None)])
    registry.register("my_package", LINUX_X86, ranges=[VersionRange("5.0.0", None)])
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("5.0.0", None)]


def test_compat_registry_unspecified_platform_python_version_must_match(
    platform_registry: CompatRegistry,
) -> None:
    assert platform_registry.get_config(pkg_name="my_package", target=T310) == []


def test_compat_registry_unspecified_platform_open_range_wins_the_union() -> None:
    registry = CompatRegistry()
    registry.register("my_package", LINUX_X86, ranges=[VersionRange("1.0.0", None)])
    registry.register("my_package", MACOS_ARM, ranges=[VersionRange("2.0.0", "3.0.0")])
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("1.0.0", None)]


def test_compat_registry_unspecified_platform_contained_range_is_absorbed() -> None:
    registry = CompatRegistry()
    registry.register("my_package", LINUX_X86, ranges=[VersionRange("1.0.0", "5.0.0")])
    registry.register("my_package", MACOS_ARM, ranges=[VersionRange("2.0.0", "3.0.0")])
    assert registry.get_config(pkg_name="my_package", target=T311) == [
        VersionRange("1.0.0", "5.0.0")
    ]


def test_compat_registry_unspecified_platform_unbounded_min() -> None:
    registry = CompatRegistry()
    registry.register("my_package", LINUX_X86, ranges=[VersionRange("2.0.0", "3.0.0")])
    registry.register("my_package", MACOS_ARM, ranges=[VersionRange(None, "2.5.0")])
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange(None, "3.0.0")]


def test_compat_registry_unspecified_platform_explicit_empty_with_other_platform() -> None:
    registry = CompatRegistry()
    registry.register("my_package", LINUX_X86, ranges=[])
    registry.register("my_package", MACOS_ARM, ranges=[VersionRange("1.0.0", None)])
    assert registry.get_config(pkg_name="my_package", target=T311) == [VersionRange("1.0.0", None)]


def test_compat_registry_unspecified_platform_all_empty_is_unsupported() -> None:
    registry = CompatRegistry()
    registry.register("my_package", LINUX_X86, ranges=[])
    registry.register("my_package", MACOS_ARM, ranges=[])
    assert registry.is_unsupported(pkg_name="my_package", target=T311)


def test_compat_registry_find_closest_version_unspecified_platform(
    platform_registry: CompatRegistry,
) -> None:
    assert (
        platform_registry.find_closest_version(
            pkg_name="my_package", pkg_version="99.0.0", target=T311
        )
        == "6.0.0"
    )


def test_compat_registry_is_valid_version_unspecified_platform(
    platform_registry: CompatRegistry,
) -> None:
    assert platform_registry.is_valid_version(
        pkg_name="my_package", pkg_version="2.5.0", target=T311
    )


def test_compat_registry_register_does_not_mutate_inputs_on_union() -> None:
    registry = CompatRegistry()
    ranges = [VersionRange("1.0.0", "2.0.0")]
    registry.register("my_package", LINUX_X86, ranges=ranges)
    registry.register("my_package", MACOS_ARM, ranges=[VersionRange("1.5.0", "3.0.0")])
    registry.get_config(pkg_name="my_package", target=T311)
    assert registry.state["my-package"][LINUX_X86] == [VersionRange("1.0.0", "2.0.0")]


########################################
#     Tests for has_package            #
########################################


def test_compat_registry_has_package_true() -> None:
    registry = CompatRegistry({"numpy": {T311: [VersionRange("1.0.0", None)]}})
    assert registry.has_package("numpy")


def test_compat_registry_has_package_true_for_unsupported_entry() -> None:
    registry = CompatRegistry({"numpy": {T311: []}})
    assert registry.has_package("numpy")


def test_compat_registry_has_package_false() -> None:
    assert not CompatRegistry().has_package("numpy")


########################################
#     Tests for _parse                 #
########################################


def test_parse_none() -> None:
    assert _parse(None) is None


def test_parse_version() -> None:
    assert _parse("1.2.3") == Version("1.2.3")


##########################################
#     Tests for canonical package names  #
##########################################


@pytest.mark.parametrize("name", ["Scikit-Learn", "scikit_learn", "scikit.learn", "SCIKIT--learn"])
def test_compat_registry_register_canonicalises_name(name: str) -> None:
    registry = CompatRegistry()
    registry.register(name, T311, ranges=[VersionRange("1.0.0", None)])
    assert registry.state == {"scikit-learn": {T311: [VersionRange("1.0.0", None)]}}


@pytest.mark.parametrize("name", ["Scikit-Learn", "scikit_learn", "scikit-learn"])
def test_compat_registry_get_config_any_spelling(name: str) -> None:
    registry = CompatRegistry({"scikit-learn": {T311: [VersionRange("1.0.0", None)]}})
    assert registry.get_config(pkg_name=name, target=T311) == [VersionRange("1.0.0", None)]


@pytest.mark.parametrize("name", ["Scikit-Learn", "scikit_learn"])
def test_compat_registry_is_valid_version_any_spelling(name: str) -> None:
    registry = CompatRegistry({"scikit-learn": {T311: [VersionRange("1.0.0", None)]}})
    assert not registry.is_valid_version(pkg_name=name, pkg_version="0.1", target=T311)


@pytest.mark.parametrize("name", ["Scikit-Learn", "scikit_learn"])
def test_compat_registry_has_package_any_spelling(name: str) -> None:
    registry = CompatRegistry({"scikit-learn": {T311: [VersionRange("1.0.0", None)]}})
    assert registry.has_package(name)


def test_compat_registry_register_other_spelling_conflicts() -> None:
    registry = CompatRegistry()
    registry.register("scikit-learn", T311, ranges=[VersionRange("1.0.0", None)])
    with pytest.raises(RuntimeError, match="already registered for package scikit-learn"):
        registry.register("Scikit_Learn", T311, ranges=[VersionRange("2.0.0", None)])


def test_compat_registry_init_canonicalises_names() -> None:
    registry = CompatRegistry({"Scikit_Learn": {T311: [VersionRange("1.0.0", None)]}})
    assert registry.state == {"scikit-learn": {T311: [VersionRange("1.0.0", None)]}}


###################################
#     Tests for range validation  #
###################################


def test_compat_registry_register_min_greater_than_max() -> None:
    registry = CompatRegistry()
    with pytest.raises(ValueError, match=r"invalid version range \('2\.0\.0', '1\.0\.0'\)"):
        registry.register("numpy", T311, ranges=[VersionRange("2.0.0", "1.0.0")])


def test_compat_registry_register_invalid_version() -> None:
    registry = CompatRegistry()
    with pytest.raises(InvalidVersion, match="not-a-version"):
        registry.register("numpy", T311, ranges=[VersionRange("not-a-version", None)])


def test_compat_registry_register_equal_bounds_is_valid() -> None:
    registry = CompatRegistry()
    registry.register("numpy", T311, ranges=[VersionRange("1.0.0", "1.0.0")])
    assert registry.state == {"numpy": {T311: [VersionRange("1.0.0", "1.0.0")]}}


def test_compat_registry_register_failure_does_not_create_package() -> None:
    registry = CompatRegistry()
    with pytest.raises(ValueError, match="invalid version range"):
        registry.register("numpy", T311, ranges=[VersionRange("2.0.0", "1.0.0")])
    assert registry.state == {}


def test_compat_registry_register_conflict_does_not_change_state() -> None:
    registry = CompatRegistry({"numpy": {T311: [VersionRange("1.0.0", None)]}})
    with pytest.raises(RuntimeError, match="already registered"):
        registry.register("numpy", T311, ranges=[VersionRange("2.0.0", None)])
    assert registry.state == {"numpy": {T311: [VersionRange("1.0.0", None)]}}


def test_compat_registry_register_failure_does_not_create_package_for_other_name() -> None:
    registry = CompatRegistry()
    with pytest.raises(ValueError, match="invalid version range"):
        registry.register("other", T311, ranges=[VersionRange("2.0.0", "1.0.0")])
    assert not registry.has_package("other")


def test_compat_registry_init_invalid_range() -> None:
    with pytest.raises(ValueError, match="invalid version range"):
        CompatRegistry({"numpy": {T311: [VersionRange("2.0.0", "1.0.0")]}})


#########################################################
#     Tests for registered strings of the boundaries    #
#########################################################


def test_compat_registry_find_closest_version_returns_registered_lower_string() -> None:
    registry = CompatRegistry({"numpy": {T311: [VersionRange("1.23.2.post1", "2.0")]}})
    assert registry.find_closest_version("numpy", "1.0.0", T311) == "1.23.2.post1"


def test_compat_registry_find_closest_version_returns_registered_upper_string() -> None:
    registry = CompatRegistry({"numpy": {T311: [VersionRange("1.0", "2.0.0rc1")]}})
    assert registry.find_closest_version("numpy", "3.0.0", T311) == "2.0.0rc1"


def test_compat_registry_find_closest_version_returns_registered_gap_string() -> None:
    registry = CompatRegistry(
        {"numpy": {T311: [VersionRange("1.0", "1.5"), VersionRange("2.0.0.post0", None)]}}
    )
    assert registry.find_closest_version("numpy", "1.7", T311) == "2.0.0.post0"
