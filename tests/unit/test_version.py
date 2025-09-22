from __future__ import annotations

import operator

import pytest
from packaging.version import Version

from feu import compare_version, get_package_version
from feu.version import filter_stable_versions

#####################################
#     Tests for compare_version     #
#####################################


def test_compare_version_true() -> None:
    assert compare_version("pytest", operator.ge, "7.3.0")


def test_compare_version_false() -> None:
    assert not compare_version("pytest", operator.le, "7.3.0")


def test_compare_version_false_missing() -> None:
    assert not compare_version("missing", operator.ge, "1.0.0")


#########################################
#     Tests for get_package_version     #
#########################################


@pytest.mark.parametrize("package", ["pytest", "ruff"])
def test_get_package_version(package: str) -> None:
    assert isinstance(get_package_version(package), Version)


def test_get_package_version_missing() -> None:
    assert get_package_version("missing") is None


############################################
#     Tests for filter_stable_versions     #
############################################


def test_filter_stable_versions() -> None:
    assert filter_stable_versions(["1.0.0", "1.0.0a1", "2.0.0", "2.0.0.dev1", "3.0.0.post1"]) == [
        "1.0.0",
        "2.0.0",
    ]


def test_filter_stable_versions_all() -> None:
    assert filter_stable_versions(["1.0.0", "2.0.1", "3.3.3", "0.9"]) == [
        "1.0.0",
        "2.0.1",
        "3.3.3",
        "0.9",
    ]


def test_filter_stable_versions_prereleases() -> None:
    assert filter_stable_versions(["1.0.0", "2.0.0a1", "2.0.0b2", "2.0.0rc3"]) == ["1.0.0"]


def test_filter_stable_versions_postreleases() -> None:
    assert filter_stable_versions(["1.0.0", "1.0.0.post1", "2.0.0.post2"]) == ["1.0.0"]


def test_filter_stable_versions_devreleases() -> None:
    assert filter_stable_versions(["1.0.0", "1.0.0.dev1", "2.0.0.dev2"]) == ["1.0.0"]


def test_filter_stable_versions_empty() -> None:
    assert filter_stable_versions([]) == []
