from __future__ import annotations

import operator

import pytest

from feu.version import compare_version, latest_version, sort_versions

#####################################
#     Tests for compare_version     #
#####################################


def test_compare_version_true() -> None:
    assert compare_version("pytest", operator.ge, "7.3.0")


def test_compare_version_false() -> None:
    assert not compare_version("pytest", operator.le, "7.3.0")


def test_compare_version_false_missing() -> None:
    assert not compare_version("missing", operator.ge, "1.0.0")


####################################
#     Tests for latest_version     #
####################################


def test_latest_version_standard_versions() -> None:
    assert latest_version(["1.0.0", "1.0.1", "1.0.2"]) == "1.0.2"


def test_latest_version_pre_releases() -> None:
    assert latest_version(["1.0.0a1", "1.0.0b1", "1.0.0rc1", "1.0.0"]) == "1.0.0"


def test_latest_version_dev_releases() -> None:
    assert latest_version(["1.0.0.dev1", "1.0.0.dev3", "1.0.0.dev2"]) == "1.0.0.dev3"


def test_latest_version_mixed_versions() -> None:
    assert (
        latest_version(
            [
                "1.0.0",
                "1.1.0.dev2",
                "1.1.0",
                "2.0.0a1",
            ]
        )
        == "2.0.0a1"
    )


def test_latest_version_epoch_versions() -> None:
    assert latest_version(["1!1.0.0", "2!0.1.0"]) == "2!0.1.0"


def test_latest_version_post_releases() -> None:
    assert latest_version(["1.0.0", "1.0.0.post1", "1.0.0.post3"]) == "1.0.0.post3"


def test_latest_version_raises_on_empty_list() -> None:
    with pytest.raises(ValueError, match="versions list must not be empty"):
        latest_version([])


###################################
#     Tests for sort_versions     #
###################################


def test_sort_versions() -> None:
    assert sort_versions(["1.2.0", "1.0.0", "1.10.0", "1.1.5"]) == [
        "1.0.0",
        "1.1.5",
        "1.2.0",
        "1.10.0",
    ]


def test_sort_versions_descending() -> None:
    assert sort_versions(["1.2.0", "1.0.0", "1.10.0", "1.1.5"], reverse=True) == [
        "1.10.0",
        "1.2.0",
        "1.1.5",
        "1.0.0",
    ]


def test_sort_versions_single_item() -> None:
    assert sort_versions(["2.0.0"]) == ["2.0.0"]


def test_sort_versions_empty() -> None:
    assert sort_versions([]) == []
