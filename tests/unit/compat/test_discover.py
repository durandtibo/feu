from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from feu.compat import (
    COMPANIONS,
    Discovery,
    PinnedDependency,
    SameVersion,
    Target,
    VersionRange,
    WheelTags,
    discover_compat_targets,
    group_into_ranges,
    is_compatible,
    tags_match_exactly,
)
from feu.compat.discover import (
    IGNORED_VERSIONS,
    _companion_judge,
    _companion_tags,
    _default_judge,
    _is_tag_compatible,
    _sorted_stable_versions,
    _tags_by_version,
)

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from feu.compat.discover import Companion

MODULE = "feu.compat.discover"

LINUX = "manylinux_2_17_x86_64"
MACOS = "macosx_11_0_arm64"
T39 = Target(python_version="3.9", os="linux", arch="x86_64")
T311 = Target(python_version="3.11", os="linux", arch="x86_64")
T312 = Target(python_version="3.12", os="linux", arch="x86_64")
T313T = Target(python_version="3.13", free_threaded=True, os="linux", arch="x86_64")
T311_MACOS = Target(python_version="3.11", os="macos", arch="arm64")


def _discover(
    wheels: Mapping[str, tuple[str, ...]],
    targets: tuple[Target, ...] = (T311,),
    *,
    requires_python: Mapping[str, str | None] | None = None,
    companion_wheels: Mapping[str, tuple[str, ...]] | None = None,
    pins: Mapping[str, str | None] | None = None,
    pkg_name: str = "pkg",
    companion: Companion | None = None,
    ignore_versions: Collection[str] | None = None,
) -> Discovery:
    def fetch_wheels(name: str) -> Mapping[str, tuple[str, ...]]:
        return wheels if name == pkg_name else (companion_wheels or {})

    with (
        patch(f"{MODULE}.fetch_pypi_wheel_filenames", Mock(side_effect=fetch_wheels)),
        patch(f"{MODULE}.fetch_pypi_requires_python", Mock(return_value=requires_python or {})),
        patch(
            f"{MODULE}.fetch_pypi_pinned_dependency_version",
            Mock(side_effect=lambda _pkg, version, _dep: (pins or {}).get(version)),
        ),
    ):
        return discover_compat_targets(
            pkg_name, targets, companion=companion, ignore_versions=ignore_versions
        )


####################################
#     Tests for is_compatible      #
####################################


def test_is_compatible_none() -> None:
    assert is_compatible(None, "3.11")


def test_is_compatible_empty_string() -> None:
    assert is_compatible("", "3.11")


def test_is_compatible_true() -> None:
    assert is_compatible(">=3.9", "3.11")


def test_is_compatible_false() -> None:
    assert not is_compatible(">=3.12", "3.11")


def test_is_compatible_invalid_specifier() -> None:
    assert is_compatible("not a specifier", "3.11")


###################################
#     Tests for group_into_ranges #
###################################


def test_group_into_ranges_open_last_range() -> None:
    assert group_into_ranges(["1", "2", "3", "4"], {"1", "2", "4"}, "4") == [
        VersionRange("1", "2"),
        VersionRange("4", None),
    ]


def test_group_into_ranges_closed_last_range() -> None:
    assert group_into_ranges(["1", "2", "3"], {"1", "2"}, "3") == [VersionRange("1", "2")]


def test_group_into_ranges_all_compatible() -> None:
    assert group_into_ranges(["1", "2"], {"1", "2"}, "2") == [VersionRange("1", None)]


def test_group_into_ranges_none_compatible() -> None:
    assert group_into_ranges(["1", "2"], set(), "2") == []


def test_group_into_ranges_single_version() -> None:
    assert group_into_ranges(["1"], {"1"}, "1") == [VersionRange("1", None)]


def test_group_into_ranges_no_version() -> None:
    assert group_into_ranges([], set(), None) == []


def test_group_into_ranges_isolated_versions() -> None:
    assert group_into_ranges(["1", "2", "3", "4", "5"], {"1", "3"}, "5") == [
        VersionRange("1", "1"),
        VersionRange("3", "3"),
    ]


########################################
#     Tests for tags_match_exactly     #
########################################

LINUX_TAG = WheelTags("3.11", False, "linux", "x86_64")


def test_tags_match_exactly_true() -> None:
    assert tags_match_exactly(LINUX_TAG, WheelTags("3.11", False, "linux", "x86_64"))


@pytest.mark.parametrize(
    "wanted",
    [
        WheelTags("3.12", False, "linux", "x86_64"),
        WheelTags("3.11", True, "linux", "x86_64"),
        WheelTags("3.11", False, "macos", "x86_64"),
        WheelTags("3.11", False, "linux", "arm64"),
    ],
)
def test_tags_match_exactly_false(wanted: WheelTags) -> None:
    assert not tags_match_exactly(LINUX_TAG, wanted)


def test_tags_match_exactly_abi3_newer_python() -> None:
    assert tags_match_exactly(
        WheelTags("3.9", False, "linux", "x86_64", abi3=True),
        WheelTags("3.13", False, "linux", "x86_64"),
    )


def test_tags_match_exactly_abi3_older_python() -> None:
    assert not tags_match_exactly(
        WheelTags("3.10", False, "linux", "x86_64", abi3=True),
        WheelTags("3.9", False, "linux", "x86_64"),
    )


def test_tags_match_exactly_abi3_without_python_version() -> None:
    assert not tags_match_exactly(
        WheelTags(None, False, "linux", "x86_64", abi3=True),
        WheelTags("3.9", False, "linux", "x86_64"),
    )


def test_tags_match_exactly_pure_python_never_matches_a_platform() -> None:
    assert not tags_match_exactly(
        WheelTags(None, False, None, None), WheelTags("3.11", False, "linux", "x86_64")
    )


####################################
#     Tests for _is_tag_compatible #
####################################

WANTED = WheelTags("3.11", False, "linux", "x86_64")


def test_is_tag_compatible_exact() -> None:
    assert _is_tag_compatible(LINUX_TAG, WANTED, None)


def test_is_tag_compatible_other_os() -> None:
    assert not _is_tag_compatible(WheelTags("3.11", False, "macos", "x86_64"), WANTED, None)


def test_is_tag_compatible_other_arch() -> None:
    assert not _is_tag_compatible(WheelTags("3.11", False, "linux", "arm64"), WANTED, None)


def test_is_tag_compatible_other_free_threading() -> None:
    assert not _is_tag_compatible(WheelTags("3.11", True, "linux", "x86_64"), WANTED, None)


def test_is_tag_compatible_other_python() -> None:
    assert not _is_tag_compatible(WheelTags("3.10", False, "linux", "x86_64"), WANTED, None)


def test_is_tag_compatible_abi3() -> None:
    assert _is_tag_compatible(WheelTags("3.9", False, "linux", "x86_64", abi3=True), WANTED, None)


def test_is_tag_compatible_abi3_too_new() -> None:
    assert not _is_tag_compatible(
        WheelTags("3.12", False, "linux", "x86_64", abi3=True), WANTED, None
    )


def test_is_tag_compatible_pure_python_allowed() -> None:
    assert _is_tag_compatible(WheelTags(None, False, None, None), WANTED, ">=3.9")


def test_is_tag_compatible_pure_python_not_allowed() -> None:
    assert not _is_tag_compatible(WheelTags(None, False, None, None), WANTED, ">=3.12")


def test_is_tag_compatible_pure_python_without_requirement() -> None:
    assert _is_tag_compatible(WheelTags(None, False, None, None), WANTED, None)


#######################################
#     Tests for the helper functions  #
#######################################


def test_tags_by_version() -> None:
    assert _tags_by_version(
        {
            "1.0": (f"pkg-1.0-cp311-cp311-{LINUX}.whl", "pkg-1.0-py3-none-any.whl"),
            "2.0": (),
        }
    ) == {
        "1.0": {WheelTags("3.11", False, "linux", "x86_64"), WheelTags(None, False, None, None)},
        "2.0": set(),
    }


def test_sorted_stable_versions() -> None:
    assert _sorted_stable_versions(
        ["1.10", "1.9", "2.0rc1", "bad", "1.0.post1", "1.0.dev1", "3.0"], ["3.0"]
    ) == ["1.9", "1.10"]


def test_sorted_stable_versions_empty() -> None:
    assert _sorted_stable_versions([], []) == []


def test_companion_tags_same_version() -> None:
    tags = {"1.0": {LINUX_TAG}}
    assert _companion_tags("pkg", SameVersion("lib"), "1.0", tags) == {LINUX_TAG}


def test_companion_tags_same_version_unknown_release() -> None:
    assert _companion_tags("pkg", SameVersion("lib"), "2.0", {"1.0": {LINUX_TAG}}) == set()


def test_companion_tags_pinned_dependency() -> None:
    tags = {"9.0": {LINUX_TAG}}
    with patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", Mock(return_value="9.0")) as mock:
        assert _companion_tags("pkg", PinnedDependency("lib"), "1.0", tags) == {LINUX_TAG}
        mock.assert_called_once_with("pkg", "1.0", "lib")


def test_companion_tags_pinned_dependency_without_pin() -> None:
    with patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", Mock(return_value=None)):
        assert _companion_tags("pkg", PinnedDependency("lib"), "1.0", {"9.0": {LINUX_TAG}}) == set()


def test_companion_tags_pinned_dependency_unknown_pinned_release() -> None:
    with patch(f"{MODULE}.fetch_pypi_pinned_dependency_version", Mock(return_value="8.0")):
        assert _companion_tags("pkg", PinnedDependency("lib"), "1.0", {"9.0": {LINUX_TAG}}) == set()


def test_companion_tags_without_companion_tags() -> None:
    assert _companion_tags("pkg", SameVersion("lib"), "1.0", None) == set()


def test_default_judge_does_not_fetch_requires_python_without_a_pure_wheel() -> None:
    with patch(f"{MODULE}.fetch_pypi_requires_python") as fetch_mock:
        _default_judge("pkg", {"1.0": {LINUX_TAG}})
        fetch_mock.assert_not_called()


def test_companion_judge_does_not_fetch_the_companion_when_platform_wheels_exist() -> None:
    with patch(f"{MODULE}.fetch_pypi_wheel_filenames") as fetch_mock:
        _companion_judge("pkg", SameVersion("lib"), {"1.0": {LINUX_TAG}})
        fetch_mock.assert_not_called()


def test_companion_judge_fetches_the_companion_once() -> None:
    pure = WheelTags(None, False, None, None)
    fetch_mock = Mock(return_value={})
    with patch(f"{MODULE}.fetch_pypi_wheel_filenames", fetch_mock):
        _companion_judge("pkg", SameVersion("lib"), {"1.0": {pure}, "2.0": {pure}})
    fetch_mock.assert_called_once_with("lib")


####################################
#     Tests for COMPANIONS         #
####################################


def test_companions() -> None:
    assert {
        "jax": SameVersion("jaxlib"),
        "polars": PinnedDependency("polars-runtime-32"),
        "pydantic": PinnedDependency("pydantic-core"),
    } == COMPANIONS


def test_ignored_versions() -> None:
    assert {"duckdb": frozenset({"0.0.0"})} == IGNORED_VERSIONS


########################################
#     Tests for discover_compat_targets #
########################################


def test_discover_compat_targets_whole_output() -> None:
    wheels = {
        "1.0": (f"pkg-1.0-cp310-cp310-{LINUX}.whl", f"pkg-1.0-cp311-cp311-{LINUX}.whl"),
        "2.0": (f"pkg-2.0-cp311-cp311-{LINUX}.whl", f"pkg-2.0-cp312-cp312-{LINUX}.whl"),
        "3.0": (f"pkg-3.0-cp312-cp312-{LINUX}.whl", f"pkg-3.0-cp311-cp311-{MACOS}.whl"),
        "3.1": (f"pkg-3.1-cp312-cp312-{LINUX}.whl",),
    }
    assert _discover(wheels, (T311, T312, T311_MACOS)) == Discovery(
        versions=("1.0", "2.0", "3.0", "3.1"),
        targets={
            T311: [VersionRange("1.0", "2.0")],
            T312: [VersionRange("2.0", None)],
            T311_MACOS: [VersionRange("3.0", "3.0")],
        },
    )


def test_discover_compat_targets_is_a_discovery() -> None:
    assert isinstance(_discover({"1.0": (f"pkg-1.0-cp311-cp311-{LINUX}.whl",)}), Discovery)


def test_discover_compat_targets_default_targets() -> None:
    with (
        patch(f"{MODULE}.fetch_pypi_wheel_filenames", Mock(return_value={})),
        patch(f"{MODULE}.fetch_pypi_requires_python", Mock(return_value={})),
    ):
        assert len(discover_compat_targets("pkg").targets) == 60


def test_discover_compat_targets_unstable_and_invalid_versions_are_ignored() -> None:
    wheels = {
        "1.0": (f"pkg-1.0-cp311-cp311-{LINUX}.whl",),
        "2.0rc1": (f"pkg-2.0rc1-cp311-cp311-{LINUX}.whl",),
        "2.0.post1": (f"pkg-2.0.post1-cp311-cp311-{LINUX}.whl",),
        "bad": (),
    }
    assert _discover(wheels).versions == ("1.0",)


def test_discover_compat_targets_versions_are_in_pep440_order() -> None:
    wheels = {v: (f"pkg-{v}-cp311-cp311-{LINUX}.whl",) for v in ("1.10", "1.9", "1.2")}
    assert _discover(wheels).versions == ("1.2", "1.9", "1.10")


def test_discover_compat_targets_no_release() -> None:
    assert _discover({}) == Discovery(versions=(), targets={T311: []})


def test_discover_compat_targets_no_compatible_release() -> None:
    wheels = {"1.0": (f"pkg-1.0-cp310-cp310-{LINUX}.whl",)}
    assert _discover(wheels).targets == {T311: []}


def test_discover_compat_targets_abi3() -> None:
    wheels = {
        "1.0": (f"pkg-1.0-cp39-abi3-{LINUX}.whl",),
        "2.0": (f"pkg-2.0-cp312-abi3-{LINUX}.whl",),
    }
    assert _discover(wheels, (T39, T311, T312)).targets == {
        T39: [VersionRange("1.0", "1.0")],
        T311: [VersionRange("1.0", "1.0")],
        T312: [VersionRange("1.0", None)],
    }


def test_discover_compat_targets_free_threaded() -> None:
    wheels = {
        "1.0": (f"pkg-1.0-cp313-cp313-{LINUX}.whl",),
        "2.0": (f"pkg-2.0-cp313-cp313t-{LINUX}.whl",),
    }
    assert _discover(wheels, (T313T,)).targets == {T313T: [VersionRange("2.0", None)]}


def test_discover_compat_targets_pure_python_wheel_uses_requires_python() -> None:
    wheels = {
        "1.0": ("pkg-1.0-py3-none-any.whl",),
        "2.0": ("pkg-2.0-py3-none-any.whl",),
        "3.0": ("pkg-3.0-py3-none-any.whl",),
    }
    requires_python = {"1.0": ">=3.8", "2.0": ">=3.8", "3.0": ">=3.12"}
    assert _discover(wheels, (T311, T312), requires_python=requires_python).targets == {
        T311: [VersionRange("1.0", "2.0")],
        T312: [VersionRange("1.0", None)],
    }


def test_discover_compat_targets_release_without_wheel_is_pure_python_if_another_is() -> None:
    wheels = {"1.0": ("pkg-1.0-py3-none-any.whl",), "2.0": ()}
    assert _discover(wheels, requires_python={"2.0": ">=3.9"}).targets == {
        T311: [VersionRange("1.0", None)]
    }


def test_discover_compat_targets_release_without_wheel_respects_requires_python() -> None:
    wheels = {"1.0": ("pkg-1.0-py3-none-any.whl",), "2.0": ()}
    assert _discover(wheels, requires_python={"2.0": ">=3.12"}).targets == {
        T311: [VersionRange("1.0", "1.0")]
    }


def test_discover_compat_targets_release_without_wheel_is_not_compatible_without_pure_wheel() -> (
    None
):
    wheels = {"1.0": (f"pkg-1.0-cp311-cp311-{LINUX}.whl",), "2.0": ()}
    assert _discover(wheels).targets == {T311: [VersionRange("1.0", "1.0")]}


def test_discover_compat_targets_ignore_versions() -> None:
    wheels = {
        "0.0.0": (f"pkg-0.0.0-cp311-cp311-{LINUX}.whl",),
        "1.0": (f"pkg-1.0-cp311-cp311-{LINUX}.whl",),
    }
    discovery = _discover(wheels, ignore_versions={"0.0.0"})
    assert discovery == Discovery(("1.0",), {T311: [VersionRange("1.0", None)]})


def test_discover_compat_targets_ignore_versions_empty_overrides_the_default() -> None:
    wheels = {"0.0.0": (f"pkg-0.0.0-cp311-cp311-{LINUX}.whl",)}
    assert _discover(wheels, pkg_name="duckdb", ignore_versions=()).versions == ("0.0.0",)


def test_discover_compat_targets_default_ignored_versions() -> None:
    wheels = {
        "0.0.0": (f"duckdb-0.0.0-cp311-cp311-{LINUX}.whl",),
        "1.0": (f"duckdb-1.0-cp311-cp311-{LINUX}.whl",),
    }
    assert _discover(wheels, pkg_name="duckdb").versions == ("1.0",)


def test_discover_compat_targets_ignored_versions_by_canonical_name() -> None:
    wheels = {"0.0.0": (f"x-0.0.0-cp311-cp311-{LINUX}.whl",)}
    assert _discover(wheels, pkg_name="DuckDB").versions == ()


########################################
#     Tests for a package with a companion #
########################################

PURE = "-py3-none-any.whl"


def test_discover_compat_targets_same_version_companion() -> None:
    wheels = {"1.0": (f"jax-1.0{PURE}",), "2.0": (f"jax-2.0{PURE}",), "3.0": (f"jax-3.0{PURE}",)}
    companion_wheels = {
        "1.0": (f"jaxlib-1.0-cp311-cp311-{LINUX}.whl",),
        "2.0": (f"jaxlib-2.0-cp311-cp311-{LINUX}.whl", f"jaxlib-2.0-cp312-cp312-{LINUX}.whl"),
    }
    assert _discover(
        wheels, (T311, T312), companion=SameVersion("jaxlib"), companion_wheels=companion_wheels
    ).targets == {T311: [VersionRange("1.0", "2.0")], T312: [VersionRange("2.0", "2.0")]}


def test_discover_compat_targets_same_version_companion_from_the_registry() -> None:
    wheels = {"1.0": (f"jax-1.0{PURE}",)}
    companion_wheels = {"1.0": (f"jaxlib-1.0-cp311-cp311-{LINUX}.whl",)}
    discovery = _discover(wheels, pkg_name="jax", companion_wheels=companion_wheels)
    assert discovery.targets == {T311: [VersionRange("1.0", None)]}


def test_discover_compat_targets_companion_registry_uses_the_canonical_name() -> None:
    wheels = {"1.0": (f"jax-1.0{PURE}",)}
    companion_wheels = {"1.0": (f"jaxlib-1.0-cp311-cp311-{LINUX}.whl",)}
    discovery = _discover(wheels, pkg_name="JAX", companion_wheels=companion_wheels)
    assert discovery.targets == {T311: [VersionRange("1.0", None)]}


def test_discover_compat_targets_same_version_companion_without_release() -> None:
    wheels = {"1.0": (f"jax-1.0{PURE}",)}
    assert _discover(wheels, companion=SameVersion("jaxlib"), companion_wheels={}).targets == {
        T311: []
    }


def test_discover_compat_targets_pinned_dependency_companion() -> None:
    wheels = {
        "1.0": (f"polars-1.0{PURE}",),
        "2.0": (f"polars-2.0{PURE}",),
        "3.0": (f"polars-3.0{PURE}",),
    }
    companion_wheels = {
        "9.0": (f"rt-9.0-cp39-abi3-{LINUX}.whl",),
        "9.1": (f"rt-9.1-cp311-abi3-{LINUX}.whl",),
    }
    pins = {"1.0": "9.0", "2.0": "9.1"}
    assert _discover(
        wheels,
        (T39, T311),
        companion=PinnedDependency("rt"),
        companion_wheels=companion_wheels,
        pins=pins,
    ).targets == {T39: [VersionRange("1.0", "1.0")], T311: [VersionRange("1.0", "2.0")]}


def test_discover_compat_targets_pinned_dependency_companion_without_pin() -> None:
    wheels = {"1.0": (f"pydantic-1.0{PURE}",)}
    companion_wheels = {"9.0": (f"core-9.0-cp311-cp311-{LINUX}.whl",)}
    assert _discover(
        wheels, companion=PinnedDependency("core"), companion_wheels=companion_wheels, pins={}
    ).targets == {T311: []}


def test_discover_compat_targets_pure_wheel_of_a_package_with_a_companion_never_counts() -> None:
    # pydantic 1.x ships a pure wheel next to compiled wheels: only the compiled wheels count.
    wheels = {
        "1.0": (f"pydantic-1.0{PURE}", f"pydantic-1.0-cp311-cp311-{LINUX}.whl"),
        "2.0": (f"pydantic-2.0{PURE}", f"pydantic-2.0-cp310-cp310-{LINUX}.whl"),
    }
    assert _discover(
        wheels, companion=PinnedDependency("core"), requires_python={"2.0": ">=3.8"}
    ).targets == {T311: [VersionRange("1.0", "1.0")]}


def test_discover_compat_targets_pure_wheel_of_a_package_with_a_companion_ignores_requires_python() -> (
    None
):
    wheels = {"1.0": (f"pkg-1.0{PURE}",)}
    assert _discover(
        wheels, companion=SameVersion("lib"), companion_wheels={}, requires_python={"1.0": ">=3.8"}
    ).targets == {T311: []}


def test_discover_compat_targets_companion_none_means_default_algorithm() -> None:
    wheels = {"1.0": (f"pkg-1.0{PURE}",)}
    assert _discover(wheels).targets == {T311: [VersionRange("1.0", None)]}


def test_discover_compat_targets_does_not_mutate_the_registries() -> None:
    companions = dict(COMPANIONS)
    ignored = dict(IGNORED_VERSIONS)
    _discover({"1.0": (f"pkg-1.0-cp311-cp311-{LINUX}.whl",)})
    assert (companions, ignored) == (COMPANIONS, IGNORED_VERSIONS)
