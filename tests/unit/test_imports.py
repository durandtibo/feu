from __future__ import annotations

from unittest.mock import Mock, patch

from feu import is_module_available, is_package_available

##########################################
#     Tests for is_package_available     #
##########################################


def test_is_package_available_true() -> None:
    assert is_package_available("os")


def test_is_package_available_nested() -> None:
    assert is_package_available("os.path")


def test_is_package_available_false() -> None:
    assert not is_package_available("my_missing_package")


def test_is_package_available_false_exception() -> None:
    with patch("feu.imports.find_spec", Mock(side_effect=AttributeError())):
        assert not is_package_available("my_missing_package2")


#########################################
#     Tests for is_module_available     #
#########################################


def test_is_module_available_true() -> None:
    assert is_module_available("os")


def test_is_module_available_nested() -> None:
    assert is_module_available("feu.imports")


def test_is_module_available_false_missing_package() -> None:
    assert not is_module_available("missing.module")


def test_is_module_available_false_missing_module() -> None:
    assert not is_module_available("feu.missing_module")
