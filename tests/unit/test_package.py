from __future__ import annotations

from unittest.mock import patch

import pytest

from feu.package import PackageValidator

######################################
#     Tests for PackageValidator     #
######################################


@patch.dict(PackageValidator.registry, {}, clear=True)
def test_package_validator_add_package_config() -> None:
    PackageValidator.add_package_config(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
    )
    assert PackageValidator.registry == {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}}


@patch.dict(PackageValidator.registry, {}, clear=True)
def test_package_validator_add_package_config_multiple() -> None:
    PackageValidator.add_package_config(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
    )
    PackageValidator.add_package_config(
        pkg_name="my_package",
        python_version="3.10",
        pkg_version_min="1.1.0",
        pkg_version_max="1.5.2",
    )
    assert PackageValidator.registry == {
        "my_package": {
            "3.10": {"min": "1.1.0", "max": "1.5.2"},
            "3.11": {"min": "1.2.0", "max": "2.0.2"},
        }
    }


@patch.dict(
    PackageValidator.registry,
    {"my_package": {"3.11": {"min": "1.1.0", "max": "1.5.2"}}},
    clear=True,
)
def test_package_validator_add_package_config_exist_ok_false() -> None:
    with pytest.raises(
        RuntimeError, match="A package configuration .* is already registered for package"
    ):
        PackageValidator.add_package_config(
            pkg_name="my_package",
            python_version="3.11",
            pkg_version_min="1.2.0",
            pkg_version_max="2.0.2",
        )


@patch.dict(
    PackageValidator.registry,
    {"my_package": {"3.11": {"min": "1.1.0", "max": "1.5.2"}}},
    clear=True,
)
def test_package_validator_add_package_config_exist_ok_true() -> None:
    PackageValidator.add_package_config(
        pkg_name="my_package",
        python_version="3.11",
        pkg_version_min="1.2.0",
        pkg_version_max="2.0.2",
        exist_ok=True,
    )
    assert PackageValidator.registry == {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}}


@patch.dict(
    PackageValidator.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.0.2"}}},
    clear=True,
)
def test_package_validator_get_package_config() -> None:
    assert PackageValidator.get_package_config(pkg_name="my_package", python_version="3.11") == {
        "min": "1.2.0",
        "max": "2.0.2",
    }


@patch.dict(PackageValidator.registry, {}, clear=True)
def test_package_validator_get_package_config_empty() -> None:
    assert PackageValidator.get_package_config(pkg_name="my_package", python_version="3.11") == {}


@patch.dict(PackageValidator.registry, {"my_package": {}}, clear=True)
def test_package_validator_get_package_config_empty_pkg_name() -> None:
    assert PackageValidator.get_package_config(pkg_name="my_package", python_version="3.11") == {}


@patch.dict(PackageValidator.registry, {"my_package": {"3.11": {}}}, clear=True)
def test_package_validator_get_package_config_empty_python_version() -> None:
    assert PackageValidator.get_package_config(pkg_name="my_package", python_version="3.11") == {}


@patch.dict(
    PackageValidator.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_package_validator_is_valid_version_true() -> None:
    assert PackageValidator.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(
    PackageValidator.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_package_validator_is_valid_version_false_min() -> None:
    assert not PackageValidator.is_valid_version(
        pkg_name="my_package", pkg_version="1.0.0", python_version="3.11"
    )


@patch.dict(
    PackageValidator.registry,
    {"my_package": {"3.11": {"min": "1.2.0", "max": "2.2.0"}}},
    clear=True,
)
def test_package_validator_is_valid_version_false_max() -> None:
    assert not PackageValidator.is_valid_version(
        pkg_name="my_package", pkg_version="3.0.0", python_version="3.11"
    )


@patch.dict(
    PackageValidator.registry, {"my_package": {"3.11": {"min": "1.2.0", "max": None}}}, clear=True
)
def test_package_validator_is_valid_version_min_true() -> None:
    assert PackageValidator.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(
    PackageValidator.registry, {"my_package": {"3.11": {"min": "2.2.0", "max": None}}}, clear=True
)
def test_package_validator_is_valid_version_min_false() -> None:
    assert not PackageValidator.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(
    PackageValidator.registry, {"my_package": {"3.11": {"min": None, "max": "2.2.0"}}}, clear=True
)
def test_package_validator_is_valid_version_max_true() -> None:
    assert PackageValidator.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(
    PackageValidator.registry, {"my_package": {"3.11": {"min": None, "max": "1.2.0"}}}, clear=True
)
def test_package_validator_is_valid_version_max_false() -> None:
    assert not PackageValidator.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )


@patch.dict(PackageValidator.registry, {}, clear=True)
def test_package_validator_is_valid_version_empty() -> None:
    assert PackageValidator.is_valid_version(
        pkg_name="my_package", pkg_version="2.0.0", python_version="3.11"
    )
