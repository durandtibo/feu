from __future__ import annotations

from feu import is_package_available

##########################################
#     Tests for is_package_available     #
##########################################


def test_is_package_available_true() -> None:
    assert is_package_available("os")


def test_is_package_available_nested() -> None:
    assert is_package_available("os.path")


def test_is_package_available_false() -> None:
    assert not is_package_available("my_missing_package")
