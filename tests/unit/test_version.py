from __future__ import annotations

import operator

from packaging.version import Version
from pytest import mark

from feu import compare_version, get_package_version

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


@mark.parametrize("package", ("pytest", "ruff"))
def test_get_package_version(package: str) -> None:
    assert isinstance(get_package_version(package), Version)


def test_get_package_version_missing() -> None:
    assert get_package_version("missing") is None
