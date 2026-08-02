from __future__ import annotations

from feu.compat.discoverers.utils import (
    build_compat_ranges,
    build_tags_by_version,
    group_into_ranges,
    sort_stable_versions,
    tags_match_exactly,
    target_to_wheel_tags,
)
from feu.compat.registry import VersionRange
from feu.compat.target import Target
from feu.compat.wheel_tags import WheelTags

##############################################
#     Tests for sort_stable_versions     #
##############################################


def test_sort_stable_versions_empty() -> None:
    assert sort_stable_versions([]) == []


def test_sort_stable_versions_sorts_ascending() -> None:
    assert sort_stable_versions(["2.0.0", "1.0.0", "1.5.0"]) == ["1.0.0", "1.5.0", "2.0.0"]


def test_sort_stable_versions_filters_pre_releases() -> None:
    assert sort_stable_versions(["1.0.0", "1.1.0a1", "1.1.0rc1"]) == ["1.0.0"]


def test_sort_stable_versions_filters_invalid_versions() -> None:
    assert sort_stable_versions(["1.0.0", "not-a-version"]) == ["1.0.0"]


##############################################
#     Tests for build_tags_by_version     #
##############################################


def test_build_tags_by_version_empty() -> None:
    assert build_tags_by_version({}) == {}


def test_build_tags_by_version_single_filename() -> None:
    result = build_tags_by_version({"1.0.0": ("pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",)})
    assert result == {
        "1.0.0": {WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")}
    }


def test_build_tags_by_version_multiple_filenames_per_version() -> None:
    result = build_tags_by_version(
        {
            "1.0.0": (
                "pkg-1.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",
                "pkg-1.0.0-cp312-cp312-manylinux_2_17_x86_64.whl",
            )
        }
    )
    assert result == {
        "1.0.0": {
            WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64"),
            WheelTags(python_version="3.12", free_threaded=False, os="linux", arch="x86_64"),
        }
    }


def test_build_tags_by_version_multiple_versions() -> None:
    result = build_tags_by_version(
        {
            "1.0.0": ("pkg-1.0.0-py3-none-any.whl",),
            "2.0.0": ("pkg-2.0.0-cp311-cp311-manylinux_2_17_x86_64.whl",),
        }
    )
    assert result == {
        "1.0.0": {WheelTags(python_version=None, free_threaded=False, os=None, arch=None)},
        "2.0.0": {WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")},
    }


def test_build_tags_by_version_ignores_version_with_no_filenames() -> None:
    assert build_tags_by_version({"1.0.0": ()}) == {"1.0.0": set()}


##############################################
#     Tests for target_to_wheel_tags     #
##############################################


def test_target_to_wheel_tags_basic() -> None:
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    assert target_to_wheel_tags(target) == WheelTags(
        python_version="3.11", free_threaded=False, os="linux", arch="x86_64"
    )


def test_target_to_wheel_tags_free_threaded() -> None:
    target = Target(python_version="3.14", free_threaded=True, os="macos", arch="arm64")
    assert target_to_wheel_tags(target) == WheelTags(
        python_version="3.14", free_threaded=True, os="macos", arch="arm64"
    )


def test_target_to_wheel_tags_none_os_arch() -> None:
    target = Target(python_version="3.11")
    assert target_to_wheel_tags(target) == WheelTags(
        python_version="3.11", free_threaded=False, os=None, arch=None
    )


##############################################
#     Tests for tags_match_exactly     #
##############################################


def test_tags_match_exactly_true() -> None:
    tag = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    wanted = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    assert tags_match_exactly(tag, wanted)


def test_tags_match_exactly_different_python_version() -> None:
    tag = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    wanted = WheelTags(python_version="3.12", free_threaded=False, os="linux", arch="x86_64")
    assert not tags_match_exactly(tag, wanted)


def test_tags_match_exactly_different_free_threaded() -> None:
    tag = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    wanted = WheelTags(python_version="3.11", free_threaded=True, os="linux", arch="x86_64")
    assert not tags_match_exactly(tag, wanted)


def test_tags_match_exactly_different_os() -> None:
    tag = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    wanted = WheelTags(python_version="3.11", free_threaded=False, os="macos", arch="x86_64")
    assert not tags_match_exactly(tag, wanted)


def test_tags_match_exactly_different_arch() -> None:
    tag = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="x86_64")
    wanted = WheelTags(python_version="3.11", free_threaded=False, os="linux", arch="arm64")
    assert not tags_match_exactly(tag, wanted)


def test_tags_match_exactly_none_vs_none() -> None:
    tag = WheelTags(python_version=None, free_threaded=False, os=None, arch=None)
    wanted = WheelTags(python_version=None, free_threaded=False, os=None, arch=None)
    assert tags_match_exactly(tag, wanted)


##############################################
#     Tests for group_into_ranges     #
##############################################


def test_group_into_ranges_empty() -> None:
    assert group_into_ranges([], set(), None) == []


def test_group_into_ranges_empty_with_latest() -> None:
    assert group_into_ranges([], set(), "1.0.0") == []


def test_group_into_ranges_no_compatible_versions() -> None:
    assert group_into_ranges(["1.0.0", "2.0.0"], set(), "2.0.0") == []


def test_group_into_ranges_single_version_is_latest() -> None:
    assert group_into_ranges(["1.0.0"], {"1.0.0"}, "1.0.0") == [VersionRange("1.0.0", None)]


def test_group_into_ranges_single_version_not_latest() -> None:
    assert group_into_ranges(["1.0.0", "2.0.0"], {"1.0.0"}, "2.0.0") == [
        VersionRange("1.0.0", "1.0.0")
    ]


def test_group_into_ranges_contiguous_open_upper_bound() -> None:
    assert group_into_ranges(["1.0.0", "1.1.0", "2.0.0"], {"1.0.0", "1.1.0", "2.0.0"}, "2.0.0") == [
        VersionRange("1.0.0", None)
    ]


def test_group_into_ranges_contiguous_closed_upper_bound() -> None:
    assert group_into_ranges(["1.0.0", "1.1.0", "2.0.0"], {"1.0.0", "1.1.0"}, "2.0.0") == [
        VersionRange("1.0.0", "1.1.0")
    ]


def test_group_into_ranges_non_contiguous_yields_multiple_ranges() -> None:
    assert group_into_ranges(["1.0.0", "1.1.0", "1.2.0", "2.0.0"], {"1.0.0", "2.0.0"}, "2.0.0") == [
        VersionRange("1.0.0", "1.0.0"),
        VersionRange("2.0.0", None),
    ]


def test_group_into_ranges_trailing_incompatible_version_closes_run() -> None:
    assert group_into_ranges(["1.0.0", "1.1.0", "2.0.0"], {"1.0.0"}, "2.0.0") == [
        VersionRange("1.0.0", "1.0.0")
    ]


##############################################
#     Tests for build_compat_ranges     #
##############################################


def test_build_compat_ranges_empty_versions() -> None:
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    assert build_compat_ranges([], None, [target], lambda _version, _target, _wanted: True) == {
        target: []
    }


def test_build_compat_ranges_empty_targets() -> None:
    assert (
        build_compat_ranges(["1.0.0"], "1.0.0", [], lambda _version, _target, _wanted: True) == {}
    )


def test_build_compat_ranges_all_compatible() -> None:
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    result = build_compat_ranges(
        ["1.0.0", "2.0.0"], "2.0.0", [target], lambda _version, _target, _wanted: True
    )
    assert result == {target: [VersionRange("1.0.0", None)]}


def test_build_compat_ranges_none_compatible() -> None:
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    result = build_compat_ranges(
        ["1.0.0", "2.0.0"], "2.0.0", [target], lambda _version, _target, _wanted: False
    )
    assert result == {target: []}


def test_build_compat_ranges_per_version_predicate() -> None:
    target = Target(python_version="3.11", os="linux", arch="x86_64")
    result = build_compat_ranges(
        ["1.0.0", "1.1.0", "2.0.0"],
        "2.0.0",
        [target],
        lambda version, _target, _wanted: version != "1.1.0",
    )
    assert result == {
        target: [VersionRange("1.0.0", "1.0.0"), VersionRange("2.0.0", None)],
    }


def test_build_compat_ranges_multiple_targets() -> None:
    target_linux = Target(python_version="3.11", os="linux", arch="x86_64")
    target_macos = Target(python_version="3.11", os="macos", arch="arm64")

    def is_compatible(version: str, _target: Target, wanted: WheelTags) -> bool:
        return wanted.os == "linux" or version == "2.0.0"

    result = build_compat_ranges(
        ["1.0.0", "2.0.0"], "2.0.0", [target_linux, target_macos], is_compatible
    )
    assert result == {
        target_linux: [VersionRange("1.0.0", None)],
        target_macos: [VersionRange("2.0.0", None)],
    }


def test_build_compat_ranges_predicate_receives_wanted_wheel_tags() -> None:
    target = Target(python_version="3.11", free_threaded=True, os="linux", arch="x86_64")
    seen: list[WheelTags] = []

    def is_compatible(_version: str, _target: Target, wanted: WheelTags) -> bool:
        seen.append(wanted)
        return True

    build_compat_ranges(["1.0.0"], "1.0.0", [target], is_compatible)
    assert seen == [WheelTags(python_version="3.11", free_threaded=True, os="linux", arch="x86_64")]
