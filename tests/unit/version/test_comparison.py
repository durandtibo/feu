from __future__ import annotations

import operator

from feu.version import compare_version, sort_versions

#####################################
#     Tests for compare_version     #
#####################################


def test_compare_version_true() -> None:
    assert compare_version("pytest", operator.ge, "7.3.0")


def test_compare_version_false() -> None:
    assert not compare_version("pytest", operator.le, "7.3.0")


def test_compare_version_false_missing() -> None:
    assert not compare_version("missing", operator.ge, "1.0.0")


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
