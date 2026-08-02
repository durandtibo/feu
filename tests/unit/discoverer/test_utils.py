from __future__ import annotations

from feu.compat.registry import VersionRange
from feu.compat.target import Target
from feu.compat.wheel_tags import WheelTags
from feu.discoverer.utils import (
    build_tags_by_version,
    sort_stable_versions,
    tags_match_exactly,
    target_to_wheel_tags,
    versions_to_ranges,
)

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
#     Tests for versions_to_ranges     #
##############################################


def test_versions_to_ranges_empty() -> None:
    assert versions_to_ranges([], None) == []


def test_versions_to_ranges_empty_with_latest() -> None:
    assert versions_to_ranges([], "1.0.0") == []


def test_versions_to_ranges_single_version_is_latest() -> None:
    assert versions_to_ranges(["1.0.0"], "1.0.0") == [VersionRange("1.0.0", None)]


def test_versions_to_ranges_single_version_not_latest() -> None:
    assert versions_to_ranges(["1.0.0"], "2.0.0") == [VersionRange("1.0.0", "1.0.0")]


def test_versions_to_ranges_multiple_versions_open_upper_bound() -> None:
    assert versions_to_ranges(["1.0.0", "1.1.0", "2.0.0"], "2.0.0") == [VersionRange("1.0.0", None)]


def test_versions_to_ranges_multiple_versions_closed_upper_bound() -> None:
    assert versions_to_ranges(["1.0.0", "1.1.0"], "2.0.0") == [VersionRange("1.0.0", "1.1.0")]
